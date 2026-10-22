# T03 mapping-S1 续审报告 1（ZCode / GLM-5.3，原会话内继续，非新任务）

- 原会话 `session_0a2c4afdc82a7ff337650697c1ad0140`；原 turn `turn_59381397-d861-4161-9acd-96bba4c8c1ef` 已由官方记录确认 completed（续审附件第 3 行所记）。本续审 turn 实际 ID 不可在任务内观测，留空由 owner 从 UI 补独立收据。
- 原报告 `mapping-S1-zcode-full-report.md` 19751B/SHA256 `f8b937a36c4879c79c57c1bb744728fa0eb124e16c7d02d56c4b0822ef858066` 与首终态 `task-actual.json` 原样保留（已复核）。
- 续审输入：`build/review-session/metadata/mapping-S1-zcode-followup-1-input.md`，12 行/3306B/SHA256 `f4ce5d04f04d454eb6d10fb91aa2939c034a20ce2a65152a4dbb3e9b7c5c6db1`，核验一致并全文读。
- 本方设置收据：`build/review-session/metadata/owner-ui-settings-followup-1.json`（2026-10-22T17:32:48Z 同会话 UI 读回：GLM-5.3/最高/完全访问；未读全局配置/日志/其他任务）。运行时实际模型 `account:bigmodel-individual-coding-plan/GLM-5.3`。
- 本报告为唯一新写面；新元数据 `task-followup-1.json`；新 raw 轮次 `zcode-followup-1-package/`、`zcode-followup-1-sources/`。原件均未覆盖。

## 1. 续审执行记录

| 步骤 | 结果 |
| --- | --- |
| 原 230 行输入真实全文 Read | 单次 Read 工具调用，编号 1–231 全覆盖（文件 230 行 + 结尾空行）；身份 41592B/`0da4d866…57a4` 复核不变 |
| HEAD/工作区 | 全程 detached `0fb8e045ec776da6e8dc1b306c72212982114cd8` 不变；唯一改动仍为授权未暂存 AGENTS.md（15147B/`de15f6ce…`）；未切分支/stage/commit/push |
| `npm run package:dir`（本树隔离 env，后台） | **exit 0**；raw/zcode-followup-1-package/（argv/时间/exit/stdout 13797B stderr 记录完整）；产出 `release/mac-arm64/OntoLearn Studio.app`（unsigned dir） |
| 包内冻结 argv 探针 | `<engine> --mapping-probe` → **exit 0**，stdout 与源码 `project-probe-first.json` **逐字节一致**（11 cases/版本/exactFacts），stderr 0B；`--mapping-probe untrusted-input.xlsx` → **exit 2**，stderr 固定 `MAPPING_PROBE_INVALID_ARGUMENTS`，stdout 0B |
| 包内锁/许可证 | `_internal/provenance/uv.lock` SHA256 == 源 `uv.lock` == `9f5b6d2b…1152e`；4 个许可证文件 SHA 全部与 `project-dependency-verification.json` 一致 |
| `npm run verify:sources` | **exit 0**，"已核对 12 个归档源文件"，stderr 0B |
| 未运行 | `npm run check`（首轮已在本树复跑 exit 0/638TS/1110Py/0skip；本轮输入未变，不重跑）；`npm run test:e2e`、C1/native/focus（仍待根窗口）；I02_HMR、未签 native caller/runner/专票研究（原禁区未触碰）；`verify-packaged-probe.py` 脚本本身未运行（其会回写 docs/reviews/T03 原证据文件，违反不覆盖原件；已用等价的直接探针+比对替代） |

## 2. 完整工程覆盖登记（138 条非 docs 路径；docs 工具与证据链首轮已全覆盖）

### 全文语义读（本轮新增 19 + 首轮 18 + 根配置 = 38 路径）
- 首轮已全读（18 delta + 根 pyproject）：mapping 四模块、entrypoint.py、engine pyproject、build-engine.mjs、uv.lock（基线 diff）、renderer mapping×3、测试×5、equipment.csv、verify-packaged-probe.py。
- 本轮新增全文：`storage.py`（1230 行全）、`rdf_snapshot.py`、`invalidation.py`、`__main__.py`、`protocol.py`、`storage_probe.py`、`contract_probe.py`、`resources.py`、`csp.ts`、`preload/index.ts`、`App.tsx`、`main/index.ts`、`window-security.ts`、`trusted-document.ts`、`view-navigation.ts`、`window-recovery.ts`、`engine.ts`、`main/jsonl.ts`、根 `package.json`（scripts 全）、`electron-builder.yml`。

### 结构性语义读（模块用途+API 面+导出/定义清单，逐路径登记）
- `task-service.ts`（TaskService 生命周期/恢复/订阅结构 40+ 成员清单）、`task-presentation.ts`、`task-progress.ts`（头+接口）、`contracts/src/v2.ts`（导出面）、`contracts/src/index.ts`（头 30 行+行数）、`contracts/python/contract_v2.py`（头+12 定义）、`coordinator.py`/`worker.py`/`job_store.py`/`memory_guard.py`/`process_environment.py`（docstring+定义计数；I03/I04 责任路径，T03 未触碰，基线 diff 为证）。
- v2 契约 JSON×8：有效性+顶层键+registry `productRuntime:['health']`（映射无产品运行时能力注册，与全部声明一致）；载荷未逐行读。
- 测试：engine 21 个非 mapping 测试、unit 15 个非 mapping 测试、e2e 5 文件——文件级登记+首轮 check 实跑通过；语义详审属各自迭代（I01–I04）责任，T03 完整树范围内不因其产生新意见（见 §4）。
- scripts 其余 4（verify-sources/verify-i01/verify-i04-package/prepare-i04-fixture/i04_matrix_evidence）docstring 级；.github 4 文件、eslint/vitest/playwright/tsconfig 配置、渲染壳三小文件（main.tsx/env.d.ts/index.html，<300B 无业务逻辑）。
- 真实未读（如实登记）：`package-lock.json`（224KB 锁产物，身份核验）、`schema/fixtures/binding-regressions/frame-fixtures/dependencies/states` 载荷（契约数据，contract_probe 实测全部通过）、`design/prototypes/*.pen`（1.4MB 设计原型资产，UTF-8 文本但非工程代码，产品验收无关）、style.css/tokens.css（样式，首轮 mapping.css 已读）。

### 首轮既有的 docs 覆盖不变
18 delta 证据文档、首失败链、PRD FR-300–304/D/G.1/§10–12、M0 S1 节、历史矩阵、共享包 5 件身份——见原报告 §3，未重复罗列。

## 3. 逐意见处置（原报告 Z1–Z6）

### Z1（原 P3）——重判为 **P4 观察，S1 范围内无缺陷，关闭为"存储层语义已确定"**
本轮全文读 `storage.py` 后，原"取决于 T01 Store 唯一性约束、语义未定义"的保留不再成立：
- `_check_slot`（storage.py:608-633）：同一 (subject,predicate) 槽上任何**非本 owner** 行若 `id == digest([s,p,value])` 即抛 Ownership Conflict——而事实 id 是内容导出（storage.py:245-257），故**对其他 owner 墓碑（object=None）重新提出完全相同三元组，墓碑行 id 恰等于新事实保留 id，提交在事务内被整批拒绝**（_replace_mapping 先 _check_slot 再写，storage.py:684-691；冲突经事务回滚，无半批）。
- 对墓碑释放槽位写**不同值**（多值谓词）：不冲突——墓碑仅是来源记录，槽位已释放；单值谓词另有 `_validate_single_slots`（仅计 object IS NOT NULL）保证同槽至多一个活值。
- 本映射自有墓碑由 DELETE+重插为全新受管行，与 preview 层 MANUAL_DRIFT（自有墓碑/漂移）闭环一致。
残余缺口仅为 UX 级：preview（plan.py:310-329）不预显"同值跨 owner 墓碑复活"这一提交期冲突，用户会在提交时而非预览时看到。原子性与冲突安全完整，FR-304"检测到冲突暂停提交"仍被执行。处置：不改 S1 产品；建议随 T00/T01 接线把该 ownership Conflict 映射为可读预览/提交提示。

### Z2（P3，维持）——renderer 预检不含重复 predicate/引用列；引擎 `_validate` 已硬拒；按 integration-request 第 2 条在 wire 层做字段级错误映射即可，无需本轮改动。

### Z3（P4，维持）——openpyxl 私有 `fs._worksheet_path`；固定 3.1.5 缓解；升级断点提示保留。

### Z4（P4，维持）——XLSX 三遍读取；Q5 未设线不量化，口径一致。

### Z5（P4，维持且已闭环）——ruff format 计数含 .md 透传；182↔207 差异=候选后 6 个 docs 提交新增 .md；本轮复跑 207 稳定、零违规；`ruff check --show-files`=48 py+2 pyproject。结论不变，非产品差异。

### Z6（P4，维持）——CSV 严格行宽 vs XLSX 补空为有意设计；正式文档接线时向用户说明。

### Z7（本轮新增，P4，信息性）
`storage.py:41-48` Conflict 错误码映射表中无 `ownership` 类别 → Store 层所有权冲突若按现状跨界会落 `INTERNAL_ERROR`。T03/测试范围内该异常仅在进程内被 pytest 断言，未跨界，无现行缺陷；与 Z1 处置同路：T00/T01 接线时为 ownership 类别定义公共错误码（或保持进程内），不自行新增公共 schema（本轮遵守"不新增公共 schema"）。

### 全树补读未发现新的 P1/P2/P3
首轮 18 路径 + 本轮 38 路径全文与结构补读中，架构不变量逐项复核成立：CSP 唯一源且生产无 unsafe-inline/eval（csp.ts）；preload 仅业务命名方法、无通用通道（preload/index.ts）；IPC sender/mainFrame/可信文档三重校验+有限路由表（main/index.ts:137-179）；fixture 仅主进程 argv+env+zod strict；渲染端 sandbox/无 Node；引擎监督注册表哈希钉死、环境白名单不继承凭据、stderr 只计 16KiB 不转发（engine.ts）；Python/TS 两侧严格 JSONL（protocol.py/jsonl.ts）；错误跨界仅固定码+messageKey+受限参数（safe_error/资源）；invalidation 仅 invalidation-v2.json、config 不失效；SQLite 唯一可变真相、正式写入仅 Store.commit、历史表 SQL 触发器防改写；App.tsx 未挂载 MappingPage、registry productRuntime 仅 health——"存储是内部 API、产品能力仅 health"的仓库级声明与代码一致。

## 4. 各门重判（原验收不变，按完整证据更新）

| 门 | 首轮 | 本轮重判 |
| --- | --- | --- |
| 静态（完整工程语义审读） | 通过（18 delta 全读+866 身份） | **通过**（补至 38 全文+138 全登记；无新 P1/P2/P3；Z1 关闭为 P4） |
| 运行（check：lint/类型/638TS/1110Py/构建） | 通过（本树复跑 exit 0） | **通过**（维持首轮实测；输入未变不重跑；本轮另证 verify:sources exit 0） |
| 打包（unsigned macOS27 arm64 目录包 CLI） | 声明范围通过（旧包+字节同一） | **升级为本树实证通过**：本树新包构建 exit 0 + 冻结 argv 探针与源码逐字节一致 + 拒绝参数 exit 2 + 包内锁/许可证 SHA 全匹配。303 新增 OOXML/CSV 边界仍为源码级（探针为固定合成样例，不覆盖 socket 零调用/限额用例）——定性不变，未冒充 |
| 父业务（App/bridge/Job/Store 正式接线） | 未实现/无法验证 | **不变**（registry/preload/App 复核确认未注册） |
| 两 OS/干净设备/签名安装/GUI | 未验证 | **不变**（GUI/native/focus 仍待根窗口；本轮未启动任何 GUI） |
| 生产/发布 | 未到；push/PR/CI 门关闭 | **不变** |

## 5. 未验边界（与首轮一致，另加）
1–7 同原报告 §8（T00/T01/T02/T08/T10 接线、双 OS、签名、生产、CI/合并、Q5、coverage-matrix 明细行与外部 350MB 归档未开）。
新增说明：engine 运行时模块（coordinator/worker/job_store）与全部非 mapping 测试为本轮结构性覆盖+首轮实跑，其逐行语义审属 I01–I04 各自门禁，T03 完整树范围内未因它们产生新意见；如 owner 要求对这些路径同样逐行全文终读，需另行指派（本轮如实登记为结构性覆盖）。

## 6. 终态

S1 私有子范围结论**较首轮增强**：源码门（全树语义覆盖）、运行门（首轮实测+本轮 sources）、打包门（本树新包+冻结 argv 实证）均通过；Z1 经 storage.py 全文重判关闭为 P4 观察；新增 Z7（P4 信息性）。无任何 P1/P2/P3 遗留。候选声明的父业务/双 OS/GUI/签名安装/生产边界继续开放，push/PR/CI/合并门保持关闭，等待 MiniMax 同版审查与 owner 全文读回处置。本续审不继承、也不授予整体通过；未修改任何源码/测试/锁/配置/验收，未新增公共 schema。
