# T09-S1 replacement-r1：ZCode GLM-5.3 全新完整独立审查报告

- 报告角色：ZCode 只读独立审查（replacement-r1 全新任务，不复用旧任务结论）。
- 审查区间：base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → product `76596656908ed84e577e8202a602e3256d5febcc`（tree `8b646570108026a8deabe8330c548cab0280122d`）全部 55 文件；流程证据 overlay `d96924e715a1b2139a75b70aea40fc30ae1129fe`；公共 review HEAD `72aa83a80a973a3edeb62ed95518bf1a22178985`。
- 本报告路径：`docs/reviews/T09/replacement-r1/zcode-glm53.md`；raw：`docs/reviews/T09/replacement-r1-runtime/zcode/raw/`；scratch：`docs/reviews/T09/replacement-r1-runtime/zcode/scratch/`。

## 1. 任务来源、身份与设置回执

身份与设置**仅**采自本方映射指定的单份 fresh 操作员本人 UI 回执 `docs/reviews/T09/replacement-pair-r1-20261023/s1-zcode/operator-own-receipt.json`（1692 B）：

| 项 | 值 |
| --- | --- |
| sessionId | `session_1d54a3bdcdcb436f5693f8a1f6c41544` |
| originalTurn | UNKNOWN（回执自身声明仅操作员后续窄路线可补） |
| 受理 | `rootStartReceived=true`、`acceptedByOfficialUI=true`；`officialMenuSIDReadBack=true`、`unsentDraftCleared=true` |
| acceptedAtUTC | UNKNOWN（回执明示不推断） |
| UI 读回 | model GLM-5.3 / effort 最高 / permission 完全访问；projectName `T09-S1-ZCode-review-7659665`；CWD 与本方 owncwd 一致；HEAD `72aa83a8…` |
| 附件绑定 | fullInput 75876 B，SHA-256 `e7bc2a15…88ea`，与本人原生附件（`pasted-text-20261023-050346-4fa678ab.txt`，409 行）逐字节一致 |

完整输入精确副本 `full-input.md` 与附件哈希一致；本方映射 `replacement-mapping.json` SHA `85efab5c…0067`（3389 B）相符。provider/model registry 级后台读回按规则不可发现，相应字段以上述 UI 回执为准标注来源；未调用 `agent list`/`session get`/全局 config/日志/peer 发现，未读取旧 round-1 报告、对方冻结 prompt 正文、旧 dispatch-runtime 的 task-settings/setup/raw/scratch/metadata。`.mimosa` 元数据仅路径/lstat。

## 2. 绑定与完整性核验（审查前后各一次）

- owncwd `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-s1-zcode-review-7659665`，detached HEAD `72aa83a8…`；base/product/process 均为真实 commit；product tree `8b646570…`。product→HEAD 仅新增 docs（证据与冻结输入），未触及任何产品源路径；base→product 恰 55 文件、38162 行新增。
- `full-source-bytes.json`（869 tracked）：以 `core.quotepath=false` 重核后 **869/869 blob 与 HEAD 一致，非 overlay 文件工作区 SHA 零漂移**；唯一 overlay 为受保护 `AGENTS.md`（15147 B，SHA `de15f6ce…c8c4`，保持 M 未暂存，未修复/未 stage/未还原）。注：首轮脚本因取错字段与 ls-tree 中文路径转义报 869 不匹配，已查明为解析问题并更正；`verification-summary.json` 一度 BAD 为手抄哈希笔误，shasum 复核与 d969 blob/manifest 三方一致。
- 32 个产品源/数据路径工作区 SHA 与 input-manifest 逐项一致；fixtures manifest（`aaaef2c0…c39e`）17 输入逐文件一致并绑定 PRD SHA `7586b2c4…0fbb`（工作区 PRD 相同）；cases=50、coverage=50；process 证据 42 文件对 d969 blob 一致；frozen-round-input 8 文件一致；`npm-check-ui-final.txt` SHA `210d3d9b…41e5`、`learning-ui-verification.json` `0cf7c7af…6c23`、两张截图 SHA 均核验通过。
- 审后终检：`git status` tracked 仅受保护 AGENTS M；新增未跟踪全部在本方允许写面（replacement-r1 报告/raw/scratch）。产品源码/测试/内容差异为空。

## 3. 完整范围逐项覆盖

按 input-manifest 55 文件 + 证据 overlay 全部实际读取/核对（不止摘要或 UI）：

1. **引擎实现**：`learning/{__init__,baselines,service}.py`、`scripts/verify-product-baselines.py` 全文。reset 只导出不写库；`verify()` 完整性（覆盖目录内全部文件、重复 JSON 键、非有限数、路径逃逸/symlink 拒绝）、17 输入 digest、PRD 源绑定、coverage↔PRD 原文包含校验、50 唯一计划、`productRuntime:not-executed`；`store_seed_plan` 点号 ID、E.5 双产能场景不含 expected/replay；`seed_test_project` 仅全新项目经 `Store.commit`，拒绝覆盖。`LearningService`：Context/Attempt 不变量（`type(x) is int` 拒绝 bool）、四档辅助单调合并、hint/agent-full-assistance 失效语义、evidence 强校验（context/check_id/evidence_id/provenance=`persisted-domain-tool`/status/完整 canonical 归一化比较，集合字段排序保重复、事件/轨迹/轮次保序，true≠1）。
2. **三份引擎测试**全文：baselines（真实 rdflib 解析/固定查询、G-behavior false 保持与 B-10 E-M4→E-M3、B-11 双通知、E.5 八轮完整 orders/consumption/actionTrace/scheduledFutureEvents/指标、manifest 防篡改 tmp_path 副本、CLI 非零退出、四基线真实 Store 重建+拒绝覆盖+无 expected、M-03 手工备注与防泄露断言）；service（无模型完整课程/术语、独立成功须逐检查实际调用、辅助归因、跨身份/过期状态/伪造证据负例、同数错对象、true≠1、集合序归一与轮次保序、非法输入与 adapter 崩溃不吞噬）；jobstore（preview rollback-only 零正式写入、真实 stdio worker test.atomic、收据/planHash/幂等重试、重开 dependencyVector 与快照、stale-preview/worker-failure/product-mode 三负例无半提交）。
3. **Renderer 五文件 + 两份 TS 测试**全文（css 另核无 url/@import/http 外部引用）：`presentation.ts` 单调水位/等版冲突 fail-closed/无效值不污染可恢复水位；`LearningWorkspace.tsx` 先记录后揭示（回执不符不显示提示文本）、同 attempt 跨 input 水位聚合（`currentFloor` project/task/attempt 维度）、generation/project key 重挂载 + `live` ref 迟到丢弃、全程 React 文本渲染无 `dangerouslySetInnerHTML`、固定中文错误、无 Node/IPC/模型/持久化，actions 全经 props 注入（App/bridge 确未接线）；16 浏览器用例（failHint 不泄露敏感文本、伪造独立拒绝、newer-lower/same-version-conflict/contradictory-newer、同 attempt 换 input、迟到 task/attempt/input/project+generation、恶意 img 标签零执行零网络请求、390px 无横向溢出）+18 纯投影用例。
4. **内容与 fixtures**：course.json（9 任务×4 级提示+完成条件+常见错误+知识点，六模块顺序、迁移与报告任务）、glossary.json（23 术语三层解释，开放世界/定义域/值域 vs SHACL）、transfer-inputs.json（102 缺名+参考清单、201 断言 vs 推理、Agent 完整代做负例）、checks.json（54 检查、课程引用全覆盖、无外联）、G-base/G-map-empty/G-behavior/E.5/cases/conventions/coverage 与 5 CSV+RQ（cases 50 项全部 `input-and-expectation-prepared-runtime-pending`，M-04 与 G-list-09 同 SHA 引用 `equipment-updated.csv`，E.5 案例 behaviorVersion=`e5-behaviors-1` 与 E.5.json 一致）。checks.json（882 KB）按结构化核对+关键对象抽查处理，未逐行读入。
5. **文档与证据**：handoff/learning-ui-contract/user-acceptance/status/recovery、三份独立内审、operation-policy 收据、全部验证 JSON 与最终 check 原件（664 Vitest/1094 pytest 全文读回）、小体积首败原件；历史 gzip 归档按 SHA 登记核对（历史索引已含原始/归档双侧哈希，未解压重读全文）。
6. **PRD 依据**：FR-003、FR-100~105、9.4、11.2、12.1、附录 C/D/E/G 相关段全文读回；E.5 固定模型与测试逐轮预期一致（产能 3：3/6/9/12、积压 W004/W007-008/W010-012/W013-016；产能 4：4/8/12/16 清空、重放一致）。

## 4. 本轮实际运行（真实整数退出码，raw 全量落盘）

收据：`raw/run-receipt.json`。退出码取每条命令的直接子进程 wait 状态（逐条 printf），无管道末命令/摘要成功掩盖。

| # | 命令（cwd） | 退出码 | 结果 |
| --- | --- | --- | --- |
| 1 | `python3 scripts/verify-product-baselines.py`（真实树） | **1** | `Manifest does not cover complete content/fixture file set` |
| 2 | 同上（HEAD 字节镜像 `scratch/mirror`，`git archive HEAD`） | **0** | 17 文件、manifest `aaaef2c0…`、50 计划、not-executed |
| 3 | `uv run --frozen pytest <三学习文件> -q`（真实树） | **1** | 38 failed / 4 passed，全部 `baselines.py:65` 同一 ValueError |
| 4 | `<.venv>/bin/python -m pytest <三学习文件> -q`（镜像，PYTHONPATH=镜像 src） | **0** | **42 passed**（2.68s，含 7 真实 I04 通道） |
| 5 | `npx --no-install vitest run learning`（真实树，未设 opt-in） | **0** | 18 passed / 16 skipped（浏览器组件恒 skip，不计通过） |

**直跑失败根因（环境事件，非产品缺陷）**：mimosa hook 在本审查会话 05:11:11 向 `tests/fixtures/product-baselines/.mimosa/hook-state/session_1d54a3bdcdcb436f5693f8a1f6c41544.json`（218 B，mode 600）写入会话状态；该路径被 `.gitignore:26 .mimosa/` 忽略故 git 不可见，但被 `verify()` 的 rglob 完整性检查正确拒绝——防篡改设计按预期工作。按规则本方仅 lstat，未读取/解析/删除；镜像对照（.mimosa 不存在、manifest/PRD SHA 相同）下同一命令全部通过，归因唯一且可复现。处置建议见发现 E-01。

**保留的 hook 拒绝**：(a) Bash heredoc 写 runner 被拒 → 改 Write 提交；加固后的字面量参数 runner 又两次被候选码扫描以路径穿越/命令注入模式拒绝（实质为对守卫函数与 `shell=False` 字面量调用的模式误报）→ **停止自写 runner 路径**，改为直跑三条预授权命令；(b) vitest 显式文件路径形式被拒（已知"只读路径误判为写源码"）→ 采用环境既定名称过滤形式 `vitest run learning`（与冻结输入记载的首败命令同形）。两条拒绝均未以包装方式重演原被拒对象。

**未运行边界**：`npm run check` 全链未机械重跑（同字节冻结原件 SHA 已核并全文读回）；带 opt-in 的 16 项 headless 组件未跑（已知 `chromium_headless_shell-1248` 缺失，不安装 runtime、不以 skip 充通过）；Electron/e2e/native/HMR、产品启动、package:dir、真实领域执行器、付费 API、密钥、CI/远端均未运行。证据分级：静态/纯投影（本轮实跑通过）/真实 I04 基础设施（镜像 42 含 7 项）/headless 组件（本轮 skip，强度取冻结 664 全量原件）/领域执行（not-executed）/package（未触发）/真人（无）。

## 5. 本轮发现

范围内产品代码、内容与测试逐文件审查未发现新的 P0–P2 缺陷。以下为环境/流程观察：

- **E-01（P3，环境）**：mimosa hook 将会话状态写入受审 fixture 目录，令本会话一切依赖 `verify(ROOT)` 的直接运行失败。产品无需改动；建议总控/操作员在审查结束后按环境清理程序移除该未登记文件（属环境产物，非受审实现变更），并考虑 hook 状态目录选址避开受审输入目录。若后续会话需直跑验证，先 lstat 检查该目录纯净度。
- **E-02（P3，流程）**：直跑失败与冻结证据的表面不一致必须显式归因（本报告第 4 节已做）；避免后续把同类环境失败误判为产品回归。

## 6. 13 项旧问题独立重判（从固定源码/原件重新判定，不复制旧结论）

| 编号 | 本轮结论 | 独立依据 |
| --- | --- | --- |
| CONTENT-01 | **已关闭** | course.json 迁移任务 instructions 无"供水泵/102/名称为断言"；答案仅在各自 L4；跨题断言（repair L4 无 201、classify L4 无 102）实测于 `test_retracted_mapping_object_keeps_manual_fact_and_transfer_has_no_answer_in_body`；镜像 42 通过 |
| CONTENT-02 | **已关闭** | M-04 steps 与 G-list-09 relink 均显式引用 `equipment-updated.csv` + `sourceSha256 f513469a…e171`，与实际文件 SHA 一致（本方核验） |
| CONTENT-03 | **已关闭** | cases behaviorVersion 集合 {behaviors-1, B07-behavior-1, e5-behaviors-1}；E.5 基线案例与 E.5.json `behaviorVersion=e5-behaviors-1` 相同（json 核对+测试断言） |
| CONTENT-04 | **已关闭** | M-03 手工备注挂 002；expected 保留 manual 且 002 无其他谓词（cases 内容+测试精确断言） |
| CONTENT-05 | **已关闭** | E.5 expected 两产能×4 轮完整 created/completed/backlog/计数/consumedEvents/actionTrace/scheduledFutureEvents/facts；测试逐轮断言与 PRD E.5 表一致；manifest `aaaef2c0…` |
| INFRA-01 | **已关闭** | `store_seed_plan` 点号 ID（`G-base.ontology/.initial` 等）；jobstore 测试断言 canonical `result_project.get`、dependencyVector `layer:id`、重开读回、planHash/收据行、幂等重试；镜像 42 通过（含 7 真实 stdio 通道） |
| UI-01 P1 | **已关闭** | `presentation.ts:112-165` 单调 floor + 等版 fingerprint 冲突；`currentRecord` 双重水位校验；newer-lower/same-version-conflict/contradictory-newer 三浏览器变体 + 纯测试（含导航离开返回仍拒绝） |
| UI-02 P1 | **已关闭** | `LearningWorkspace.tsx:242-281` 无 context 迁移任务全拒、缺 `recordHint`/保存失败/回执不符（版本不严格更高、辅助低于水位）均不揭示文本；failHint 用例并断言不泄露异常文本 |
| UI-03 P1 | **已关闭** | `currentFloor`（LearningWorkspace.tsx:61-76）按 project/task/attempt 跨 input 聚合 hint/assistance，具体结果仍按四元组隔离；hint4→input2 独立记录被拒（浏览器实测） |
| UI-04 P1 | **已关闭** | 矛盾新版保留于投影、`conflictVersion` 非 null 时 fail-closed，不回退旧 pass；`invalidates-old-pass` 纯测试 + `contradictory-newer` 浏览器变体（旧"独立迁移成功"失效、进度回 0/2） |
| UI-05 P2 | **已关闭** | `observeRecord` 仅将有效 0..4 提示、safe 版本、已知辅助类别纳入水位（无效 maxHint5 归零不污染）；无效最新仍令投影不可用，合法新版本恢复（blocks-invalid 纯测试） |
| DOC-01 | **已关闭** | recovery.json/learning-ui-verification.json/status.md 当前版明确 765/d969 指向与新摘要；本方核 42 份 process 文件对 d969 blob 一致，旧记录保留未覆写 |
| DOC-02 | **已关闭** | opt-in 口径（未设 1 恒 skip、设 1 缺 runtime 为 launch 失败）写入 contract 与 verification `explicitOptIn`；viewport 390×844 与截图文件 390×1932 分记；sandbox 仅声明 launch 配置+成功（`assuranceBoundary` 不外推）。本轮未设 opt-in 实测 16 skipped 佐证 |

## 7. 三项 P3 总控延期（独立判断）

| 编号 | 判断 | 独立理由 |
| --- | --- | --- |
| S1-OBS-01 导出回执守卫缺组件断言 | **接受延期** | 核对属实：`exportReport` 通知仅按 `sameContext && exported` 呈现（LearningWorkspace.tsx:308-325），测试确无缺能力/`exported:false`/异迟 context 三类组件断言。T10 未接线前无真实导出通道，组件行为 fail-closed（不显示成功、按钮禁用/不可用提示），无正确性风险；T10 正式接线验收前补齐的触发门合理。当前不视为已覆盖。 |
| S1-OBS-02 两迁移任务 1/2 级提示区分度 | **接受延期** | 核对属实：两迁移任务 hints 1/2/3 文本完全相同（仅 L4 各异）。属内容区分度质量项：提示本身正确、不误导、不泄露答案，四级渐进与归因语义完好；冻结题目不可在本候选内修改，后继内容候选增强并双方全新完整审查的条件合理。 |
| S1-OBS-03 checks 内联 E.5 oracle 一致性缺自动断言 | **接受延期** | 核对属实：三份引擎测试均未断言 `checks["G-list-01"].expected.capacities` 与 `E.5.json expected` 相等；本方 json 深比较显示当前两者**完全一致**（此为审查者手工核对，不构成产品防线，不据此宣称关闭）。漂移风险在下一次内容/oracle 维护前无自动检测；"下次维护前补完整对象、顺序、双 replay 直接一致断言"的延期条件合理，且总控未将其标为已修。 |

三项延期均维持"当前有界 S1 非阻断"，未发现需上调严重度或转为必验缺失的新证据。

## 8. PARENT-01/02/03（保留，不关闭）

- PARENT-01：多阶段阶段契约/正式接线门保留——765 未实现 T00/T01 阶段契约，`Context.input_version` 绑定聚合检查当前终态的边界已在 handoff §多阶段证据如实声明；独立树 stage 原型（12699cc/245718/e651 等）不在本输入，未拼入。
- PARENT-02：G-list-02 仍为 exactFile/exactPointer 及冲突计划（非完整 round DTO 比较器）；当前课程 scenario 用展开 G-list-01/06（实测课程 checks 引用恰为此两项）；A-10 仅三个固定反例，完整指定评估集仍 T08 依赖。未宣称关闭。
- PARENT-03：跨窗口/重开/跨 attempt 辅助不可洗需 T01/T08 真实持久账本；renderer 临时 floor 与纯 reducer 非权威（contract 与代码注释均如实声明）。未登记父功能通过。

其余父门未闭清单（与本方审查一致，S1 通过不关闭）：T02–T07 真实领域执行器与阶段证据、T01 durable 学习记录/跨 attempt 账本/业务命名 bridge 与 App 正式路由（content.ts 仅静态导入，无接线属实）、课程与 fixture 入包、T08 真实完整代做来源、T10 实际报告/项目包导出、Windows/macOS、≥5 名真实新手 80% 原口径、CI/远端/push/PR/merge 与 57 项 P0 原门。

## 9. 最终结论

**通过**。限定范围：T09-S1 replacement-r1 同版冻结候选（base 5f910b5 → product 765 全部 55 文件，含固定内容/基线/学习纯服务/受控 I04 基础设施/隔离学习组件），流程证据取 d969 overlay。理由：

1. 完整区间逐文件审查未发现范围内阻断缺陷或必验缺失；13 项旧问题经本轮独立重判全部"已关闭"且证据成立；3 项 P3 延期经独立判断全部接受且不关闭父门；PARENT-01/02/03 保留。
2. 本方独立运行与冻结证据一致：HEAD 字节镜像 verify exit 0（17 输入/manifest aaaef2c0/50 计划/not-executed）、镜像学习专项 42 passed（含 7 真实 I04）、无 opt-in vitest 18 passed/16 skipped；同字节全量冻结原件（664 Vitest/1094 pytest/构建/ruff）SHA 核验并全文读回。真实树直跑失败已确证为 hook 会话文件污染（防篡改检查正确触发），非产品缺陷，不构成不通过依据。
3. 身份链成立（fresh 本人回执、附件字节/SHA 绑定、CWD/HEAD 一致），关键证据齐备，无"无法验证"项；不写条件 Pass。
4. 未以 S1 通过关闭任何父门/发布门；push/PR/CI/merge 由总控与开发线按原门执行，本审查者未做任何写源/提交/推送操作。

## 10. 终态绑定

- 本报告为本任务 terminal 输出；落盘后由操作员按本人窄路线读取绑定并记录哈希。
- 审查前后源码一致性：tracked 零漂移（唯一 M 为受保护 AGENTS.md，未 stage，SHA `de15f6ce…` 不变）；本方写入仅限本报告与 replacement-r1-runtime/zcode/{raw,scratch}。
- 附：报告哈希见操作员读回记录；raw 清单与逐文件 SHA 见 `raw/run-receipt.json`。
