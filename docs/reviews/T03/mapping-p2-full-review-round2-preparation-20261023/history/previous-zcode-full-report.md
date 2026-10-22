# T03 mapping P2 全新完整独立静态审查报告（ZCode / GLM-5.3）

- 报告写面：本树 `build/review-session/reports/mapping-P2-zcode-full-report.md`（唯一新写面之一，另见 `metadata/task-actual.json` 的非伪填更新）。
- 审查性质：全新指定外审，不继承旧 303 会话或旧 Pass，不读取对方本轮（MiniMax）任何意见/进度/raw/metadata；仅按授权读取已封存历史 Z1–Z7/F01–F11 材料。
- 本轮零产品修改、零 commit/push/stage、零切分支、零产品命令运行（含 check/package/e2e/GUI/native/HMR）；工具自动拒绝原样保留，未以脚本或换工具绕过。

## 0. 结论先行

**判定：在本次实际完成的静态审读与既存证据复核范围内通过——未发现新的 P0/P1/P2 产品缺陷；18 项历史意见经我方逐项独立源码复核全部定性成立（含两处必须纠正的原报告表述：Z1 续报"preview 不预显同 ID 墓碑冲突"的残余说法不成立、F06 的"合法 XML 中不可能出现字面 DOCTYPE"普遍结论不成立）；Z2 维持 P3（私有 UI 预检局限，后端 fail-closed，属 T00/T01 接线待办而非本候选产品缺陷）。六新增边界 case 与 17 项固定包证据链完整、边界表述精确无夸大。**

分列门判定（不以局部 Pass 替代整体）：

| 门 | 判定 | 依据 |
| --- | --- | --- |
| 源码静态（完整工程语义审读） | **通过**（覆盖登记见 §3，含如实登记的部分覆盖类别） | 全部产品源码全文读 + 18 项定点复核 + 架构不变量逐项成立 |
| 单元/check（既存证据引用） | **通过（引用，非本轮重跑）** | 固定 1116 Py/638 TS exit0 原件；本轮无变更不重跑 |
| 包 CLI（固定 17 case） | **通过（既存实际包证据，发生在原 P2 树）** | 见 §5；不得写成在本树重新构建/执行 |
| GUI / e2e / native / CUA | **未验证**（本轮明确不运行；native/STOP 禁区未触碰） | — |
| 两 OS / 干净设备 / 签名安装 | **未验证** | 仅 macOS-27 arm64 未签名目录包证据 |
| 父 57 P0 / 跨模块 / 正式接线 | **未通过 / 未完成**（非本候选子范围） | registry productRuntime 仅 health；MappingPage 未挂载 |
| CI / 远端 / 生产 / push/PR | **未验证 / 门保持关闭** | 无新运行；指定双审未齐 |

## 1. 任务来源、实际设置与身份（不伪填）

| 项 | 实际值 | 来源 |
| --- | --- | --- |
| 派发输入 | `build/review-session/metadata/dispatch-prompt.md`，44835B，SHA256 `8106610dac75122b6846c8050e5352f51bd90319179dee838c26ffc372fc1abf` | 官方 Read 工具单次全文读取至 EOF（243 行，无截断），哈希实测一致 |
| 本方 UI 设置来源 | `operator-own-ui-pre-submit.json`（1137B，SHA256 `3ce8760b…3ad8`，实测一致） | 同目录唯一 owner 本方来源；未做 agentlist/session-get/global config/数据库/peer 查询 |
| 请求设置 | GLM-5.3 / 最高 / 完全访问（yolo） | 上文件 projectUI=T03-Mapping-P2-ZCode-c1e44、modelUI=GLM-5.3、thinkingUI=最高、permissionUI=完全访问 |
| 实际任务身份（owner 已回填） | sessionId `session_3d7a3bc7be217561ee227f6415e78e50`、turn `turn_2be6c154-5b67-4845-8176-1dc5ec55616e`（sentCount 1 / acceptedCount 1，nativeModel GLM-5.3 匹配，status `ACCEPTED_FULL_INPUT_NATIVE_MATCH_TERMINAL_UNKNOWN`） | `metadata/task-actual.json`（owner 2026-10-22T20:56:02Z 回填；本报告撰写时读回）；backend effort/permission 标量仍 UNKNOWN，如实保留 |
| 唯一 cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping-P2-zcode-review-da1795` | 实测 |
| 实际 HEAD | `c1e44f81723f9c616f669f56481d1b1ada7e57f2`（detached） | `git rev-parse HEAD` 实测 |
| 批准 base / 修复 base / 产品候选 / 证据源 | `5f910b52c69d86a1076b2032e5d3c63e715947f3` / `30319412daf8ae4745987babf7bbed93c53b6b42` / `da1795b20c3c0d47ae975fe3371e802092a4b429` / `4ec492f07d261164283a939c65b5e835c30e561e` | 实测核对，未以 repairbase 替代批准 base |
| AGENTS 保护覆盖 | 15147B，SHA256 `de15f6ce…7c8c4`，保持 unstaged（`git status` 仅 ` M AGENTS.md`） | 实测；Git 树内旧 blob 不是覆盖实际值 |

**现场核验实测命令**（全部只读）：`git rev-parse HEAD`、`git status --porcelain`、`git log --oneline -6`、`shasum -a 256`（dispatch/operator/tree-index/AGENTS/P2 包各件/产品源码/根 pyproject）、`git show <ref>:<path> | shasum -a 256`（30319412/da1795/c1e44f81/5f910b52 四 ref）、`git diff --stat`（303→da1795、da1795→c1e44f81）、对共享包固定 ref `ed9cef96…` 经 T03-mapping 仓库只读 `git show` 取两件身份、多文件 Read/cat 全文读取。未运行任何产品/构建/测试命令；未执行生成器或安装器（`environment.sh` 仅读，未 source 执行 owner setup driver）。

**关键实测结果**：

1. 30319412→da1795 非 docs 差异恰为 `mapping/probe.py`（+184 行）与 `tests/test_mapping_entrypoint.py`（+73 行）两文件；da1795→c1e44f81 非 docs 差异为空——"完整 HEAD 仅追加文档、与产品候选非 docs 逐 blob 相同"声明成立。
2. P2 包核心身份全部实测匹配：actual-receipt 28825B/`5ad2ea0f…`、oracle 3123B/`e7a8c0d3…`、probe.py 13911B/`219d6581…`、test 5647B/`30d2abe6…`、source/plan/entrypoint/uv.lock/package-lock/build-engine.mjs/electron-builder.yml/根 pyproject 与 candidate-binding 11 条 identity 逐条相等（含我方一次误读的自我纠正：binding 第 8 条路径是根 `pyproject.toml` 494B/`55674b4f…`，四 ref 同值；`packages/engine/pyproject.toml` 424B/`09b4f2c2…` 三 ref 一致未变但未单列于 binding，见 §7 Obs-1）。
3. requirements.csv 59 行 = 55 精确 P0 + 2 带注释 P0（FR-005、FR-302）+ 2 P1（FR-506、FR-903），与派发口径一致；acceptance-baselines.csv 50 行在册。
4. 共享包固定 ref 身份：`candidate-manifest.json` 4301B→`60c52bd1…`、`mapping-S1-fixed-inputs.json` 241447B→`ddbeeb21…`（git show 实测）；本树 legacy-fixed-package 两件副本逐字节同哈希。
5. preparation-tools-v2 两件原字节副本与其 manifest 哈希一致；`make-dispatch.py.raw` 静审见 §3.6。

## 2. 审查范围执行情况（不缩成两文件 delta）

### 2.1 完整工程（180 engineering 项分类）

`full-candidate-tree-c1e44f81.json`（273638B/`a8afd363…` 实测一致，1028 项 = 180 engineering + 848 documentation_or_evidence）解析后逐类覆盖：

| 类别 | 覆盖方式 | 明细 |
| --- | --- | --- |
| 引擎 Python 源码 16 模块 + entrypoint | **全文读** | mapping/{probe 373 行,source 298 行,plan 390 行,__init__}、storage.py 1230 行、job_store.py 1529 行、coordinator.py 659 行、worker.py 273 行、protocol.py、invalidation.py、invalidation-v2.json、rdf_snapshot.py、resources.py、memory_guard.py、process_environment.py、__main__.py、__init__.py、storage_probe.py、contract_probe.py、entrypoint.py |
| mapping 专项测试 4 件 | **全文读** | test_mapping_entrypoint（12 项，含 -O、三拒参、guard 恢复/故障/吞异常、位置负例）、test_mapping_source（21 项）、test_mapping_plan（22 项）、test_mapping_recovery（9 项） |
| desktop main/preload/renderer | **全文读** | main/index.ts、csp.ts、engine.ts 538 行、task-service.ts 887 行、jsonl.ts、window-{security,recovery}、trusted-document、view-navigation、preload/index.ts、App.tsx、mapping/{MappingPage.tsx,model.ts,mapping.css}、task-progress.ts、main.tsx、env.d.ts、index.html；task-presentation.ts 结构性读（纯展示文案映射） |
| contracts | **全文读** | src/{index,v2 572 行,states-v2,dependencies-v2,design-v2}.ts、python/contract_v2.py 507 行、v2/{registry,errors,dependencies,states}.json；schema.json(123KB)/fixtures.json(472KB)/binding-regressions(124KB)/frame-fixtures(17KB) 为数据载荷——**结构级覆盖**（键/枚举/关键 $defs 抽验；运行时由 contract_probe+双端测试全量执行，未逐字散文通读，如实登记） |
| 构建/CI/配置/锁 | **全文读/身份级** | package.json、根/engine pyproject、build-engine.mjs、electron-builder.yml、electron.vite.config.ts、eslint.config.mjs、.prettierignore、vitest/playwright/tsconfig、.github/ci.yml 及 3 件、.editorconfig/.gitattributes/.npmrc/.node-version/.python-version、scripts/{verify-sources.mjs,verify-i01.py,verify-i04-package.py,prepare-i04-fixture.py}（全文）、i04_matrix_evidence.py（19.8KB 结构级）；uv.lock/package-lock.json **身份级**（23393B/`9f5b6d2b…`、224331B/`a462ba70…`，与 binding 相等；锁内容不逐行读） |
| tests/unit、tests/e2e 非 mapping 件 | **部分覆盖（如实登记）** | t03-mapping-state.test.ts 全文；其余 14 unit + 5 e2e（task-service/task-runtime/supervisor/csp-lifecycle/desktop/i04-jobs/native-* 等）本轮未逐行重读——理由：base→da1795→HEAD 对这些文件零差异，且其为 I01–I04 各迭代门禁责任、在既往指定轮次已全量审读/实跑；本轮以 `git diff` 零差异 + 类型/用途登记覆盖。若 owner 要求对这些路径同样逐行终读，需另行安排 |
| 大数据/设计资产 | **结构/身份级** | design/prototypes/*.pen（1.4MB 设计原型）、package-lock、fixtures/binding-regressions/frame-fixtures、tests/fixtures/mapping/equipment.csv（52B，读） |
| docs 内可执行证据工具 | **全文读（本包相关）/登记（历史）** | 本包 verify-packaged-boundaries.py 281 行、independent-review/audit.py 185 行、run-command.py（p2-original-raw 副本）、owner/{make-dispatch,freeze-scope,prepare-environment}.py、F01 所指 docs/iterations/T03/verify-packaged-probe.py（:15–16/:66 定点+全文）；I02/I03 归档 .mjs/.py.txt 探针（~25 件）登记为已封存历史证据工具（既往轮次审读，本轮未重读全文，身份经 tree index 固定） |

### 2.2 全部原输入/历史

- 两份历史终态报告全文读毕：Z 方 79 行（`54c0c041…` 索引声称一致）、M 方 393 行（`4ab6e2c6…`）、technical-disposition-draft 58 行；handoff-index.json 在册。
- historical-findings-index.{md,json} 全文读；18 真实编号确认，无"原 15 问题"清单构造。
- 共享包固定 ref 两关键件身份经只读 git show 复核（§1.4）；legacy-fixed-package 副本逐字节一致；旧 866 项入口/coverage-matrix/historical-stage-inventory 在树副本登记（1.1MB 矩阵为结构级，既往轮次已逐项）。
- 旧 failed/HOLD/首失败链保留确认：P2 包 74 原件含 ruff 首败（exit1 ×2）、targeted 首败 1 failed/11 passed（stdout 1489B 在册）、check-first 等 T03 目录原件登记。

### 2.3 完整需求与原验收

- PRD `docs/prd/PRD-本体学习与落地Agent工作台.md` 1255 行**全文读毕**（一次 Read 至 EOF）：59 FR、57 P0（含 2 带注释）、附录 A–G 全部、§10–12 全部、G.1 M-01–M-06、E.5 固定模型、D.2 九行失效表、Q1–Q10 待决项。FR-300–304 仅作映射局部定位，未当全范围。
- control-snapshots：requirements.csv（59 行实测分布见 §1.3）、acceptance-baselines.csv（50 行）、developer-common-instructions/desktop-operation-policy/external-review-permissions（随 dispatch 全文附读）、plan/tasks/controller-handoff/review 结构登记。
- M0 计划 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` 207 行**全文读毕**（S1/S2/S3/C1/B1/U1 六节全文）；docs/m0-checklist.md 全文（35 行）；ADR-0001/0002/0003/0004 登记为结构级（其内容已由 M0 计划 §S1–S3 与既往评审覆盖，本轮未逐字重读，如实登记）。

### 2.4 无法完成的部分（明确声明）

848 件 documentation_or_evidence 中，除上列全文读对象外（T03 证据链核心件、两报告、索引、README、M0/PRD 等），I01–I04 各迭代目录的历史证据档案（约 640 件）本轮**未逐件重读**，按固定 blob 身份 + 既往两轮指定审查覆盖登记引用（M 方 followup 曾 866/866 逐路径登记、749 全文）。受限 SDK/witness/descriptor/index 身份载荷及 STOP 现场（T03-native-location-N0-build）按原权限**未读/未触碰**，仅按 fixed manifest 登记未验；不据此排除父门。

## 3. 新 P2 六项与 17 项固定包证据复核

### 3.1 实现真实性（源码级，本轮独立审读）

- `probe.py:214–275 _external_workbook`：手工构造最小合法 OOXML——external-cached-formula 为 B2 `t="str"` 公式 `WEBSERVICE("https://example.invalid/ref")` + `<v>只读已保存值</v>` 缓存；external-hyperlink 为 B2 inlineStr 显示文本 + `_rels/sheet1.xml.rels` 中 `TargetMode="External"` 关系。无 caller URL/path/值。✓
- `probe.py:278–343 _boundary_cases`：CSV 四类以真实 caps 常量生成超限输入（`source.py:11–15` 实测 8MiB/64MiB/50000/256/32768 与 oracle limits 相等），捕获 `SourceError.issue` 后比较**完整 (code,sheet,row,column)**，不符即 `CSV_BOUNDARY_LOCATION_MISMATCH` fail-closed；外部引用两 case 要求精确两格值并断言 `not any(calls.values())`。✓
- `probe.py:191–211 _socket_guard`：替换 `socket.socket/create_connection/getaddrinfo`，先计数再抛 `RuntimeError`，`finally` 恢复三原对象；`run()`（:346–364）中依赖 `import_module("openpyxl")` **在 guard 之前**（有注释声明），guard 覆盖全部固定输入构造与解析，legacy 后与每新 case 后各有零计数断言；计数为同一 invocation 累积快照。✓ 与 delivery/receipt 的边界表述逐点一致。
- `entrypoint.py:6–16`：`--mapping-probe` 严格单参数（多余参数 exit2 + 固定 `MAPPING_PROBE_INVALID_ARGUMENTS\n` 32B stderr，实测三个拒绝流同哈希 `1b643286…`）；内部异常转 `MAPPING_PROBE_FAILED` exit1，不泄原始异常。`_require` 用显式 RuntimeError，`-O` 下不失效。✓
- 测试（产品 delta 第二文件）：12 项含 `[],["-O"]` 双模式完整 serialized oracle 断言、三拒参、monkeypatch 三 API 故障/吞异常/guard 恢复、**位置负例**（篡改 file-limit 的 row=1 → 断言 `CSV_BOUNDARY_LOCATION_MISMATCH`，证明非预写文案比对）。首次失败链（targeted 1 failed/11 passed）保留于 raw。✓

### 3.2 证据链与边界精确性

- oracle 冻结时序成立：`oracle-before-run.json` 记 2026-10-22T18:40:45（authoredBeforeNewProbeImplementationAndExecution:true，basis 为固定 303 原 11 项期望 + 六项测试规格），全部受控命令自 18:42:29 起、verifier 18:47:19 启动；oracle 哈希 `e7a8c0d3…` 全链一致，无从 stdout 反写。
- `verify-packaged-boundaries.py`（281 行静审）：固定 argv 五命令、严格 `json.loads(stdout)==expected` 全量语义等值（重复键/非有限数拒绝、64KiB 上限）、source==package、reject stderr 逐字节断言、PYZ code 对比仅递归归一化 co_filename（marshal4/optimize0）、包内符号链接逃逸与特殊文件拒绝、引擎执行前后身份复查、全新输出目录。无 caller 输入。
- receipt（28825B 副本=原件字节）：17 条 allCaseRecords 全 `assertionMatched`；`independentPerCaseProcessExit:null`、`executionDomain:"one mandatory17case invocation"` 如实登记；两个成功 case 的 `column:2` 是已知 B2 fixture 坐标（probe 硬编码登记，非错误定位列）；四 CSV case 为真实 issue 完整定位（""/0/0、CSV/1/0、CSV/2/1、CSV/50002/0——行号语义经我方按 `_table` 计数规则独立核算：header=1、数据行自 2 起、50001 条数据行的越界行恰为 50002）✓。
- 收据内旧 cwd/argv/时间全部指向原 P2 树 `…/T03-mapping-p2-boundaries`，未伪称本树重跑；本树 setup 收据 `packageExecuted:false`。✓
- codeBindings 三模块 sourceCodeSha256==actualPackageCodeSha256（probe `ad1ddd07`/source `007f5b8a`/plan `d6f64766`）；440 项 inventory、包内 lock=`9f5b6d2b…`、4 许可证 SHA 与 project-dependency-verification 相符（独审 audit.py 独立重算 + 我方源码级复核其校验逻辑，二者一致）。
- 1116 算术：固定 303 时代 1110 中 entrypoint 为 6 项，新候选扩至 12 项（parametrize 展开），1110+6=1116 自洽。
- 次要观察（不影响结论）：verify 脚本 :214 以 csv-row-limit-located 的 socketCalls 快照作为全部 17 行的 `guardCallsAtEndOfSameInvocation` 标签——该 case 并非字面上的"最后"快照，因全部为 0 数值等价，仅标签语义略宽（见 §7 Obs-3）。

### 3.3 独立审计材料（既存本地 Codex 独审）

`independent-review/`（review.md/audit.py/audit-result.json/stdout）全文读毕：其"11 个 source identities 全相同"经我方重算成立；其结论仅作可复核历史材料，不构成本候选指定双 Pass。本轮我方未运行 audit.py。

## 4. 18 项历史意见逐项独立复核（本轮新判，非转抄处置草案）

| 编号 | 我方独立复核（文件:行 均本轮实读） | 本轮定性 |
| --- | --- | --- |
| Z1（首报P3→续报P4） | `storage.py:620–627`：`reserved_id=digest([s,p,v])`，同槽他 owner 行 id 等价即抛 ownership Conflict，**不受墓碑 object=None 影响**——跨 owner 同值墓碑复活在事务内整批拒绝成立（`_replace_mapping`:684–691 于 commit 事务内先 `_check_slot`）。**续报残余说法证伪**：`plan.py:310–329` 循环中 `candidate["id"]==fact["id"]`（:314）在 `fact["object"] is not None` 的 or 右支之外，preview 层对同 ID 墓碑同样报 OWNERSHIP_CONFLICT——两层都有同 ID 判定 | 报告纠正项（残余表述不成立）；产品无需修改；原严重度与改判历史原样保留 |
| Z2（P3 维持） | `model.ts:119–144 mappingDraftValid`：检查列存在（`names.has`）、IRI 形式、keys 唯一/存在、referenceColumns 存在——确无重复 predicate 与重复 referenceColumns 预检；`plan.py:118–119`（`predicate in targets` 拒绝）与 `:130–138`（reference_columns 去重校验）引擎硬拒 | **维持 P3**：私有 UI 预览前提示局限，后端 fail-closed，无越权/错误提交路径；T00/T01 wire 字段级错误映射待办。原 Z 报告"终段无 P3 遗留"与"Z2 维持 P3"的内部矛盾按历史保留，本轮以维持 P3 为准 |
| Z3（P4） | `source.py:268` `fs._worksheet_path` 私有 API 属实；依赖钉死 3.1.5 + 回归限定 | 维护性观察，留作升级断点；本轮无实际不兼容证据 |
| Z4（P4） | `parse_xlsx`:258/261 两次 `_open_xlsx` + :268 iterparse 扫描属实；"三遍"为概括描述 | 资源/性能观察，未测量不量化；Q5 未设线 |
| Z5（P4，原报称闭环） | ruff 计数为工具输出口径 | 无产品差异；不追认 182/207 全体解释 |
| Z6（P4） | CSV `_table`:96–97 `ROW_WIDTH` 严格等宽 vs XLSX :283–286 稀疏补空——两种宽度处理确不同 | 已声明有意解析差异；文档说明事项 |
| Z7（P4） | `storage.py:41–48` code 映射确无 ownership（落 INTERNAL_ERROR）；`job_store.py:94–110 _application` 将 ownership Conflict 转有界 `OWNERSHIP_CONFLICT/detailRef`（新事务落 job_details，无原文/值/路径） | 与 F11 同一接线约束；私有服务不提交，无现行跨界缺陷 |
| F01（低） | `docs/iterations/T03/verify-packaged-probe.py:15–16` 回写 stdout/stderr 两受跟踪件 + :66 回写 verification.json，路径写死无出参——属实 | 证据工具可复查性问题；**新 P2 verifier 已按新输出目录模式纠正该实践**；本轮未执行旧脚本 |
| F02（低） | `MappingPage.tsx:40–44` setField 将编辑字段移至数组尾；`model.ts:65–67` draftKey=JSON.stringify 顺序敏感；`currentPreview`:69–81 因 key 不匹配拒绝旧预览 | fail-closed UX 局限，非授权缺陷；修规范化须新候选+双新审 |
| F03（信息） | 我方实读 registry：`mapping.commit` = formal-write + requiresChangeSet/Confirmation + agentEligible:true + **implementation:design-only**；`productRuntime:['health']`；`v2Runtime` 无 mapping 方法；`coordinator.py:248–254` job.create 仅 test_mode 且限 test.read/test.atomic/test.rounds | 设计态注册元数据观察；不可派发能力成立；归 contracts owner 正式启用前统一 |
| F04（信息） | `eslint.config.mjs` ignores 不含 docs；`.prettierignore` 含 docs/reviews——实测属实 | 工具链策略不对称，非执行失败 |
| F05（验证观察） | 正面探针结果保留 | 非待修缺陷；"preview 与 Store 一致"仅限已核分支 |
| F06（验证观察+**普遍结论证伪**） | 三个普通转义样例正面结果保留；但"合法 XML 文本 `<` 必然转义故 part 不可能有字面 DOCTYPE"的普遍结论**不成立**：XML CDATA（如 `<t><![CDATA[<!DOCTYPE html>]]></t>`）可承载字面文本，而 `source.py:181–186` 对原始 part 字节做无上下文子串拦截 | 报告纠正项：区分已测普通转义样例与未测 CDATA；**未制作/运行 fixture，不宣称已证产品误拒**；DOCTYPE/ENTITY 闸为 fail-closed 安全控制，本轮不建议改动；是否属必须接收的合法输入由 root/T03 决策 |
| F07（信息） | `csp.ts:15–17` 非法 dev origin/nonce throw；`main/index.ts` whenReady 异步回调调用且至文件尾无 catch，窗口创建在其后——静态可达 dev-only 未捕获 rejection 成立；两文件 base→HEAD 未变 | 继承开发态诊断问题；交 desktop owner；非本候选引入 |
| F08（信息） | `test_i04_lifecycle_boundaries.py:235/295/343` 恰三处 `skipif(sys.platform!="darwin")`；CI quality 为 ubuntu-latest（ci.yml 实读） | "macOS 当次 1110/0skip"成立，不得发 Linux 零 skip 证书 |
| F09（信息） | `check-registered-scope.txt`:90 collected 1110；:112–115 明列 entrypoint 6/plan 22/recovery 9/source 21（=58 mapping）；:130 总 1110 passed | **原报告统计错误证实**：1110 已含 mapping 58，正确表述为"总 1110（旧），其中 mapping 58；新候选总 1116"；仅报告更正 |
| F10（信息） | `plan.py:102–108` identity 限 `[A-Za-z0-9_.-]{1,128}`（T03 路径拒非法 id）；`storage.py:344–350` 内部定义 id 仅非空校验为事实 | T03 假设消解；存储/契约粒度差异归正式接线 owner |
| F11（信息） | `job_store.py:716–754 commit_job` 经 `_application` 调 `super().commit`；:372 writing 集合含 mapping.commit；与 Z7 形成真实代码链 | 正式写入错误适配约束成立；mapping.commit 未正式接线；T01 集成时经 JobStore.commit_job 路由 |

**无"原 15 问题"清单；18 编号 ≠ 18 缺陷（F05/F06 为验证观察，F09 为报告统计错误）。** 全部原严重度/首失败/终态历史原样保留。

## 5. 本轮新登记意见（本审查新增）

| 编号 | 级别 | 位置 | 触发/影响/证据/建议 |
| --- | --- | --- | --- |
| Obs-1 | 信息（登记完备性） | `candidate-binding.json` sourceIdentities | 11 条 identity 含根 `pyproject.toml` 但未单列 `packages/engine/pyproject.toml`（T03 责任文件，424B/`09b4f2c2…`）。经 git 实测该文件 303→da1795→HEAD 逐 blob 未变，无完整性影响；建议未来 binding 对 T03 责任路径逐条单列，避免依赖 git diff 间接证明 |
| Obs-2 | 信息（测试-文档耦合） | `packages/engine/tests/test_mapping_entrypoint.py:15–20` | 测试从 `docs/reviews/T03/mapping-p2-boundaries-20261023/fixed-probe-v2-expected.json` 加载完整 oracle——该 docs 文件成为测试套件的载荷输入，移动/更名该评审包会破坏 `npm run check`。单一事实源是有意设计，但建议在包 README 标注此依赖方向 |
| Obs-3 | 信息（标签语义） | `verify-packaged-boundaries.py:214` / receipt 17 行 | `guardCallsAtEndOfSameInvocation` 取自 csv-row-limit-located 的累积快照而非字面"最后"时刻；全零下数值等价，仅标签略宽。未来可取末 case 快照或改为终检计数 |
| Obs-4 | 确认项（非缺陷） | engine 包证据来源 | 4622464B/`c4c8d80c…` 引擎及全部包内执行均发生在原 P2 树；本树无 pack/check 新结果。各方表述不得写成"新树 fresh 包"；本轮所有引用均已按此口径 |

继承未修复项维持：Z2（P3）、Z3/Z4/Z6/Z7、F01–F04、F07–F11 按上表原级开放，六新增不自动修复其中任何一项（UI 预检、正式接线、错误映射、平台证据等边界不变）。

## 6. 各门重判与未验边界

**架构不变量逐项复核成立**（本轮源码级）：本地优先（无网络/遥测/云/HTTP 端口；socket 仅固定 probe guard 计数并拒绝）；渲染端隔离（sandbox、preload 12 具名方法、无通用 invoke、IPC sender/mainFrame/可信文档三重校验、有限路由表、fixture 仅主进程 argv+env+zod strict）；CSP 唯一源 `csp.ts` 两变体、生产无 unsafe-inline/eval（生产 meta 注入 + 开发 header 同源生成）；确定性与 Agent 解耦（确定性结果仅真实引擎路径；registry productRuntime 仅 health；coordinator 限 test.*）；存储（SQLite 唯一可变真相、正式写入经 Store.commit 版本化原子提交、旧基线拒绝 `:324–329`、RDF 图仅快照重建 `rdf_snapshot.py`、不可变证据 SQL 触发器、collect_cache 不触历史/pins/current/job_current）；数据层次与失效（staleReason 仅出自 invalidation-v2.json、model 族 null 不失效、publish 事务内重验、迟到结果 historical）；模型外发（S3 前无网关无凭据，引擎与 worker 环境白名单 `process_environment.py`/`getEngineEnvironment` 不含凭据）；错误跨界（safe_error 固定码+messageKey+受限参数；worker 固定 exit 码；coordinator stderr DEVNULL；engine.ts stderr 仅计 16KiB 不转发内容）。

**未验边界（逐项明确）**：① `npm run test:e2e`/GUI/native/C1/focus 未运行（本轮按派发不运行；native/STOP/未签 caller/SDK 载荷未触碰）；② 两 OS/干净设备/签名安装/公证未验证（builder mac identity:null）；③ 父 57 P0、FR-300–304 之外的正式接线（T00 文件选择、T01 确认/ChangeSet、公共 bridge/App 挂载、I05/I06）未完成未验收；④ CI/远端核验/push/PR/合并门关闭（指定双审未齐，本报告不构成放行）；⑤ 性能/容量未测量不量化（Q5 未设线）；⑥ 848 文档件中 I01–I04 历史证据档案未逐件重读（§2.4 如实登记）；⑦ "零 socket"仅指固定解析期间三 API 计数为零，不涵盖依赖 import、预存别名或其他 OS 网络原语；三模块 code 等价不升级为全部依赖语义等价；⑧ 旧 303 双审、本地 Codex 独审、owner setup 均不构成本候选指定双 Pass。

## 7. 终态

- **本轮范围结论**：全新完整独立静态审查在 §2 登记的覆盖范围内**通过**。固定 17 项包证据、六新增边界、产品两文件 delta、18 项历史意见、完整需求/M0/验收基线均已独立复核；除 Z2（P3，接线待办）与上列开放观察外，无新 P0/P1/P2 产品缺陷；两处历史报告表述（Z1 残余、F06 普遍结论）经源码级证伪应予纠正。
- **不构成**：push/PR/CI/合并放行；父 57 P0/跨模块/两 OS/GUI/签名/生产门关闭；对另一指定模型（MiniMax）本轮任务的任何推断（未读未传）。
- 实际任务 ID/backend 标量由 owner 从应用读回后填入 `metadata/task-actual.json` 预留空位；本报告全文待 owner 读回处置。终态后不自行将任何模型不通过改写为通过。
