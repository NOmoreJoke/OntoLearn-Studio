# I03 Round 1 独立对抗性审查报告（ZCode / GLM-5.3）

## 1 评审任务、模型及思考设置的来源记录

- 任务标识：`I03-R1-ZCode-GLM53-C4-f574a72`。来源分两层如实记录：总控核验人类授权并串行预约两审查应用 UI；本 I03 派发会话随后通过 CUA 在精确 worktree/feature 分支实际创建本任务并读回 GLM-5.3/最高与运行态（据 `docs/reviews/I03/status.md`「候选4外审实际创建与控制中断（仅流程追加）」一节，45–49 行；任务明细见同目录 `tasks.json`）。本任务环境自报模型标识 `account:bigmodel-individual-coding-plan/GLM-5.3`、思考最高，属任务环境自报标签，任务内部无法独立核验派发 UI 的读回结果；本环境未提供原生 task UUID，按派发要求如实注明，不臆造。
- 实际模型：GLM-5.3（`account:bigmodel-individual-coding-plan/GLM-5.3`），思考设置：最高。与总控预约的指定设置一致，未替换模型或降低门禁。
- 独立性：本任务从头全量审查固定 base→head，未读取、未使用另一指定模型（M3.1-Flash/xhigh）本轮报告或输出的任何内容，不以其结论为依据；对其报告文件的存在性不作断言（勘误核对时仅以 `ls` 确认文件名，未打开其内容）。未运行任何 Electron/原生/HMR/产物窗口类验证；未修改实现代码、未提交、未推送、未切换分支；在仓库内仅写入本报告文件。
- 额度与操作约束遵守：仅执行纯 CLI 验证（typecheck/check/verify:sources/pytest/自写探针），原始 stdout/stderr 与真实退出码存于本机 `/tmp/i03-review-zcode/` 各独立子目录；无额度受限事件，未消费任何恢复权益。

## 2 项目路径、分支、base 与 head

| 项 | 值（实际核验） |
| --- | --- |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I03-protocol-contracts` |
| 分支 | `feature/I03-protocol-contracts`（`git branch --show-current` 实测） |
| base | `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3` |
| head | `f574a7234923f28e9356a45a17253803e7602e06`（`git rev-parse HEAD` 实测一致） |
| 提交序列 | ad9756e（契约设计）→ 6f35ffd（UTF-8 显式编码）→ 8305d20（语义错误与验证投影契约）→ 0ec24b7（可追踪 merge 合入含 I02 的 develop，实测未触碰 I03 的 36 份受审文件）→ f574a72（新基线验证文档） |
| 工作树状态 | 仅 `AGENTS.md`（他方规则修改，SHA-256 实测 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，与保护声明一致，未 stage）与 `docs/reviews/I03/` 纯流程记录未提交；未混入受审实现 |
| `git diff --check` | 通过（无空白错误） |

## 3 已检查范围、验证命令与实际结果

检查范围：base→head 全部 37 份变更文件（契约 JSON 六件、TS/Python 双端校验器、storage.py 边界守卫、双端测试、fixtures、迭代设计文档五份、评审流程与交接文档），并按验收依据（inputs/scope.md 的 I03 行与门禁、m0 计划 S1/S2/U1 全文、acceptance.md、ADR-0003-design/protocol/jobs-and-storage/shared-state、I05-semantic-boundaries、I01 ADR-0002 与 round-3 处理记录、PRD V0.6 的 8.6/8.7/10.2–10.5 及验收引用的 FR/附录对应关系）逐项核对。

实际执行的验证（均为本审查独立实跑，原始日志与退出码保存在 `/tmp/i03-review-zcode/{typecheck,check,sources,probes}/`）：

| 命令/探针 | 退出码 | 结果 |
| --- | --- | --- |
| `npm run typecheck --workspace @ontolearn/contracts` | 0 | strict 通过 |
| `npm run check` | 0 | eslint/prettier/desktop typecheck/构建/ruff 通过；TS 5 文件 420/420、Python 622/622 通过（与冻结证据声明一致，独立复核成立） |
| `npm run verify:sources` | 0 | 12 个归档源文件一致 |
| `git diff --check` base→head | 0 | 干净 |
| Python 对抗探针（自写，40+ 断言，`uv run --frozen`） | 0 | 全部符合预期 |
| TS 差分探针（同一批断言，vitest 自定义 config 挂仓库 root 运行，未写仓库文件） | 0 | 0 处不一致，与 Python 侧行为完全一致 |
| 哈希核验 | — | 两份 I05 交接快照 SHA-256 与 `I05-contract-source.json` 声明一致（ad84c439…/ea40f827…）；AGENTS.md 为受保护 SHA |

自写探针覆盖（超出交付语料的反例）：staleReason 空原因/前后版本失配/before==after/新增成员 after=0/家族不在集合摘要/重复依赖/当前态携带原因/model 依赖无码；validationProjection 断言层混入派生层、派生层缺失、重复角色、current 选择下 historical 状态、两层状态矛盾、resultId/实现/快照/约束定义失配、非推理结果、回收载荷、非约束层冒充约束身份；通知 seq 缺口、progress 版本失配、外层/DTO 项目失配、cancelling→succeeded 无最终证明拒绝；游标到期/页大小变更/token/绑定失配；依赖闭包 4095 成功、4097 越界、环去重、model 引用可被跟踪、非法 scope 拒绝；错误码未知/messageKey 互换/retryable 翻转/越界参数拒绝、五参数上限内合法。

### 机器可核对的结构一致性（本审查程序化验证）

- `errors.json` 26 码与 `schema.json` `$defs.error.oneOf` 26 分支逐字段一致（测试锁定，且我独立比对成立；勘误：原稿误记 24/24，经 `git show f574` 重数更正）；`UNSUPPORTED_CONSTRUCT` 17 枚举与 `parameterMeanings` 键完全一致；`RESOURCE_LIMIT` 8 枚举同理。
- `staleReason` 8 码与 S1 `invalidation-v2.json` 逐字一致，`model` 家族 `staleReason=null`（附录 D 第 9 行反例规则在契约层保持）。
- registry 24 项（14 个服务方法 + 10 个 job 能力）的 params/result `$ref` 全部可解析；依赖策略 7 项与 registry `dependencyPolicy` 一一对应、无孤儿；`v2Runtime=[]`、`productRuntime=["health"]`、全部能力 `implementation` 为 design-only/test-design-only，无未实现能力进入运行声明。
- `schema.json` 在双端受限词汇表内（按 compile 实际遍历方式核验，未知词汇 0 个）；所有数组节点均带显式 `maxItems`；公开身份为 UUIDv4、哈希为小写 SHA-256，`name` 模式排除空白与超长。
- 硬上界落实：帧 262144、错误 2048、页 131072/200 行/64 格/8192 标量、错误参数≤5 项、job.list≤100、limits 各字段与 protocol.md 数值一一对应；错误参数仅含固定枚举、有界整数与不透明 id/hash，无原值/路径/堆栈/自由文本。
- I05 v3 细码表：I03 文档 25 行与源交接 25 行代码集合程序化比对完全一致；历史 30 码表完整保留；五个退休合码（INPUT_LIMIT/RESULT_LIMIT/UNSUPPORTED_LITERAL/UNSUPPORTED_RDF/ASSERTED_SCOPE_REQUIRED）明确不再用于新执行分支；SHAPE_PATH_UNCLASSIFIED 仅 INTERNAL_ERROR/{}；来源归责（用户输入/可信违约/无法分类三分）逐行与交接一致。

## 4 需求覆盖核对结论（acceptance.md「I03 必须通过」逐行）

| 验收行 | 判断 | 依据摘要 |
| --- | --- | --- |
| 信封与每方法严格 | 通过 | request/response/notification 按方法 oneOf、params/result 引用齐全；314 cases + 30 responses 双端一致；数值 2.0/孤立 surrogate/CRLF 等 TS/Python 分歧已在内部审查 B1/A6 关闭并经我的差分探针复证 |
| hello、身份与响应绑定 | 通过（设计层） | bootstrap 仅一次、无交集 [2]、二次 hello INVALID_STATE、握手前 HANDSHAKE_REQUIRED；matchesResponse 绑定 id/method/session/project/job/nonce/operation/subscription；hello 成功能力必须全部 ∈ v2Runtime=[]（诚实零声明）；实际常驻握手按验收属 I04 |
| 安全错误 | 通过 | 全码正反例跨端语料；五参数、2048 字节、受限引用实测；分层（协议失败/任务失败/取消/过期/不支持）在文档与 schema 中互斥 |
| 取消与状态 | 通过 | states.json 全状态笛卡尔积正反例（双端 36 组合一致）；cancelling→succeeded 需 finalBeforeCancel 证明门；零轮 null/两轮保留/非轮次拒绝在 job 按状态分支 + semantic() 落实 |
| 真实依赖 | 通过 | dependencies.json 与 shared-state 九能力表逐项一致（含 withDerived 仅 asserted+derived、changeset 保守全集、model 家族可跟踪但不产生领域码）；deriveDependencies 双端行为一致，环去重/悬空拒绝/4096 上界经探针验证 |
| U1 | 通过 | 项目/任务/结果/current 指针/草稿/选中态身份表完整；result 分 current/stale/historical + payloadStatus=evicted；result.page 完整六字段 binding + 服务端 cursorRecord + CURSOR_MISMATCH/EXPIRED/PAYLOAD_EVICTED；job.list 双身份初始 null/后续非 null、不可变列表快照、稳定 (createdAtMs,jobId) 序 |
| S1 实际边界 | 通过 | storage.py 开库守卫显式拒绝既存 NULL/空 kind 且零清理（iterdump 比对实测）；publish/current 共用 `_result_identity`，非法 kind/实现来源零写入、合法身份唯一 current；legacy 非对象 config 统一 ValueError 且零副作用（真实 SQLite 反例） |
| S1 交接无遗漏 | 通过 | jobs-and-storage「I01 交接闭环」11 项与 I01 round-3 处理记录逐条对上（见 §6） |
| 独立审查与源输入 | 通过 | inputs/sources.json 的 6 份冻结输入 SHA 由 `test_frozen_input_hashes_are_self_contained` 锁定且我实跑通过；`verify:sources` 核对的 12 项是 `docs/source-manifest.json` 归档源清单，属另一份清单，我另行实跑通过（勘误：原稿将两者混称为"inputs/sources 12 项"）；内部审查 A/B/C 三系列均有独立关闭记录；本报告为指定双外审之一，另一模型独立进行 |
| 仓库静态与引擎回归 | 通过 | 本审查独立复跑四类命令全过；未启动任何本机窗口类验证 |

I04 必须实际完成的原验收、I05 真实语义执行、真实分层图投影/C→Mid→Equipment 反例在本候选中均如实标注未执行（fixtures 的 `validationProjectionSemantics.runtimeStatus` 明示需 I04/I05 真实集成证据），未以描述符或元数据测试冒充——符合"不能要求以替身冒充已完成"的审查边界。

## 5 发现的问题

未发现阻断或重要问题。以下 P3 项均不构成 I03 退出门槛阻断，允许延期到 I04/I05 处理；每项给出触发条件、影响、证据与建议。

### P3-1 双端纯校验器存在两处当前不可达的行为分歧模式

- 位置：`packages/contracts/src/v2.ts:45-47,72,114`；`packages/contracts/python/contract_v2.py:60,95,247-259`。
- 触发条件：仅当未来 `schema.json` 被修改——(a) 引入受限词汇表之外的关键词时，TS `compile()` 经 `fail()` 抛出 `Error('INVALID_REQUEST')` 且 `validateV2` 不捕获，Python 侧 `check()` 返回 False 且 `validate` 有 try/except 兜底；(b) 某数组节点缺失 `maxItems` 时，TS 静默采用 100000 上限，Python 无上限。
- 影响：当前 schema 我已程序化核验（未知词汇 0、所有数组显式 maxItems），分歧不可达；但未来 schema 演进若遗漏这两条不变量，双端对同一输入的接受/拒绝将悄然不一致，违背"同一公共样例接受/拒绝完全一致"的 I04 验收前提。
- 建议：在 I04 前统一失败模式（TS 捕获或返回失败 validator、数组默认上限对齐），并增加一条 schema 元测试锁定"词汇表受限、数组必须显式 maxItems"两条不变量。允许延期。

### P3-2 开库 kind 守卫在每次 Store 打开时做两次全表扫描

- 位置：`packages/engine/src/ontolearn_engine/storage.py:47-53`。
- 触发条件：每次 `Store.__init__` 对 `results` 与 `current_results` 各执行一次无索引的 `typeof/trim` 扫描（`LIMIT 1` 仅在命中违例时提前终止，无违例时全表扫完）。
- 影响：M0 spike 规模下可忽略；I04 引入真实负载后开库成本随结果行数线性增长。
- 建议：I04 接入真实数据量时评估改为迁移版本变化时一次性检查或加部分索引，并保持"显式拒绝、不静默清理"的语义不变。允许延期。

### P3-3 内部 kind 字符串允许前后空白，公开映射时须规范化

- 位置：`packages/engine/src/ontolearn_engine/storage.py:743-752`（`_result_identity` 仅对 `strip()` 后判空）。
- 触发条件：`publish`/`current`/开库守卫均接受 `" query"` 这类前后带空白的非空 kind。
- 影响：S1 内部自由字符串与本轮守卫自洽；但公开 DTO 的 `name`/kind 模式禁止空白，I04 将内部 kind 映射为公开 kind 时若不规范化，带空白的内部身份会直接穿透为公开身份或被公开层拒绝造成不可寻址。
- 建议：I04 的公开映射表层显式规范化/校验内部 kind；如需收紧守卫本身须新候选。允许延期。

### 观察记录（不计为问题，供 I04/I05 实现时注意）

1. protocol.md 描述了通知的"接收层"（seq>lastSeq、stateVersion≥已知、缺口触发 job.get）与"应用层"（连续 seq、严格下一 stateVersion）两层；本轮代码只交付更严的应用层 `acceptsJobEvent`。接收层属 I04 运行时职责，设计承接完整，非缺陷；I04 须保留两层区分，不能以应用层函数替代接收策略。
2. `job.cancel` 响应校验 `(disposition==='alreadyTerminal') !== 终态` 隐含要求服务以判定时刻（写前）快照填充 state/stateVersion——例如 queued 任务取消被立即持久为 cancelled 时，诚实响应是 (accepted, queued 判定点) 而非 (accepted, cancelled)。实现须按此语义取值，契约本身自洽。
3. `runConfig.maxActionsPerRound` 为 const 1000：动作上限已纳入 runConfig 但不可按运行调低；M0 常量选择，I04/I05 若需可变上限须新候选。
4. `validationProjectionMatchesResources` 允许 `inputSelection='historical'` 时资源 resultState='current'（显式历史选择下资源恰仍为当前），与设计文本"可读取可用历史/过期依据"一致，记录其解释边界。

## 6 历史问题关闭判断（逐项）

### I01 round-3 移交 I03 的 11 项（docs/reviews/I01/round-3/processing.md）

| 历史项 | 本审查独立判断 | 依据 |
| --- | --- | --- |
| N-R3-1 / F3-01 kind 守卫 | 已关闭（本轮已实现） | `_result_identity` 于 publish/current 共用；非法 kind 零写入（iterdump）、合法身份唯一 current、既存 NULL/空键开库显式拒绝且零清理——三项均有真实 SQLite 测试且我随全量 check 复跑通过 |
| N-R3-2 current 非法 provenance 伪装无结果 | 已关闭（本轮已实现） | 同守卫在 `current()` 前置，形状错误 ValueError 与合法未找到 null 区分，测试覆盖 None/list/int/缺键 |
| F3-02 legacy 非对象 config | 已关闭（本轮已实现） | commit_round 写前对象检查统一 ValueError，真实旧记录反例零副作用、progress/history 不变 |
| F3-03 collect_cache 全库范围与 pin 顺序 | 已关闭（契约层，实现属 I04） | jobs-and-storage 明确全库维护、显式确认、先 pin 后报告、PAYLOAD_EVICTED 语义；未新增项目清理参数（与处理记录一致） |
| F3-04 人工值恢复语义 | 已关闭（契约层） | changeSet intent 含 restore-managed-value/restore-historical-manual-value/undo-one-changeset；恢复须新显式 edits/预览/确认，不改写旧 marker |
| F3-05 ChangeSet 固定顺序 | 已关闭（契约层） | definitions→remove→edits→manual→mapping 与 JSON 键序无关、同 fact 净效果 edits、未知 fact 可审计 no-op 均显式写入 |
| F3-06 facts 项目级依赖 | 已关闭（契约层） | job/result 向量强制 facts:asserted、project 投影允许空向量；未伪造细粒度键；集合变化走 definitionSetDigests 独立机制 |
| F-07 提交后投递失败 | 已关闭（契约层） | operation.get 权威对账 + 传输失败≠提交失败 + 不自动新 operation |
| F-11 / R4 / N-07 锁与 I/O 映射 | 已关闭（契约层） | 仅 sqlite 主码 BUSY/LOCKED→STORAGE_BUSY、IOERR/FULL/READONLY/CORRUPT→STORAGE_FAILURE，禁文本匹配，未知→INTERNAL_ERROR |
| N-06 重复 finish_run/pin 幂等 | 已关闭（契约层） | 同证据幂等返回、异内容 INVALID_STATE、evicted→PAYLOAD_EVICTED，I04 服务事务内实现 |
| R6 历史增长 | 承接说明已记录（契约层）；原问题本身保持 I01 登记的开放/延期状态与原等级，不构成关闭 | 本线仅在 jobs-and-storage 记录"不以删除历史补性能"的承接约束；按 I01 round-3 处理记录，差分/压缩/容量设计留待真实负载与 Q5 目标确定后进行，该历史问题在彼时前保持开放 |

### 本会话内部审查 A/B/C 系列（候选演进中产生）

A1–A6、B1–B5、C1–C2 的修订点我均以独立探针复证：current 完整键绑定（result.current 分支）、operation/subscription 绑定、queued 零提交/success 必须 marker、页大小与稳定顺序、终态拒绝同版倒退、全串正则与数值 2.0、迭代闭包与 4096 上界、stale 原因去重与 before 对应、facts 键强制、job.create 完整 input/确认绑定、约束定义身份三分反例——全部关闭成立。旧候选 1–3 的外审意见按门禁不沿用，本轮为新 base→head 全量审查，无未关闭历史阻断。

## 7 未验证事项与证据边界

以下事项本轮未验证，均为冻结验收明确划归 I04/I05 或受本机无窗口约束的运行项；本候选也未将其声明为已完成，不因此扣减结论：

- 常驻进程、真实 JSONL reader（拆包/粘包/UTF-8/重复键/追加前字节限额）、队列/worker/取消/崩溃恢复、持久 job/marker 对账、窗口重连联验——I04。
- Python→主进程→bridge→UI 错误全链路与 PRD 8.6 四段式 UI 呈现——I04。
- 真实 RDFS/SHACL 执行、分层图投影、C→Mid→Equipment 与 x 类型真实反例、外联拒绝与打包——I05；I05 源检查点 02a8c909 本线不可达，仅交接快照哈希一致可证。
- Electron e2e/native/HMR/产物启动——本机禁止，留隔离环境。
- push/PR/远端 CI/合并、远端 develop 核验——门禁未到。
- 另一指定模型（M3.1-Flash/xhigh）本轮报告——独立进行，未读。

证据边界：纯校验器接受的是已解码 JSON 值，不证明原始帧字节、marker 真实存在、hash 对应真实 blob、权限成立或引擎计算正确——candidates 文档对此如实声明，与本审查判断一致。

## 8 最终结论

**通过。**

候选 4（base `c2f9b038…` → head `f574a723…`）在 I03 冻结范围内满足全部可现实验收：严格信封/逐方法 schema、hello 与身份绑定、安全错误目录、状态机与取消语义、真实依赖策略、U1 身份/过期/分页、S1 最小边界守卫（真实 SQLite 反例）、I01 全部历史移交项承接、源输入哈希一致；四类静态/单测/引擎验证由本审查独立复跑全过，双端适配器在交付语料之外追加的 40+ 对抗反例上行为完全一致。发现的 3 项 P3 与 4 条观察均不阻断，已给出触发条件与延期建议，供 I04/I05 处理。本通过不将任何未执行的运行项（I04 运行时、I05 真实语义、桌面联验、远端 CI）登记为完成，不改变 Q2/Q3/Q5–Q9 决策边界，亦不构成对 I05 未冻结交接或 v2Runtime 空集之外的能力承认。

——审查者：ZCode（GLM-5.3，思考最高），任务 I03-R1-ZCode-GLM53-C4-f574a72，2026-10-20。

## 附录 A：运行资源通知与日志自查（2026-10-20，报告交付后追加）

- 本审查全部验证命令（typecheck/check/verify:sources/diff --check/两批探针）均在收到"共享 build/out 已预约给另一审查任务独占"的通知**之前**完成并保存原始退出码；通知到达时报告已交付，无未结束的验证步骤。
- 按通知要求自查已有日志：`check` 完整 stdout 确认七阶段齐全（eslint `--max-warnings 0`、prettier 全过、desktop tsc、vitest 5 文件 420/420 其中 contract-v2 为 405 项、electron-vite main/preload/renderer 三段构建成功、ruff 与 format 通过、pytest 622/622），exit=0 且 stderr 为空；contracts typecheck、verify:sources（12 项）、Python/TS 探针的 exit 码均为 0。TS 探针 stderr 仅含 Vite 对 `/tmp` 配置文件的 ESM/CJS `configLoader` 迁移警告，非失败。日志内容与本报告 §3 声明逐项一致，无需修正。另勘误（见附录 B）：我对本报告文件执行 `npx prettier --check` 的退出码 0 属实，但报告路径位于 `.prettierignore` 的 `docs/reviews` 忽略范围（`--file-info` 显示 `ignored:true`、`inferredParser:null`），退出 0 源于被忽略而非内容经过格式校验；上文 check 阶段的"prettier 全过"指仓库内未被忽略文件的 `format:check`，属实际校验，两者不同，本报告文本本身未经 prettier 内容格式检查。
- 自本通知起不再运行或读取任何依赖共享构建输出的命令；此前 `npm run check` 的 build 阶段写入发生在预约生效前且已结束。若后续确需构建类验证，将先请派发方重新预约。
- 本通知不用于推断另一审查任务的任何进度或结论；f574a72 全范围、GLM-5.3/最高、禁止本机测试窗口、不读另一模型本轮产物、不改候选等原约束继续有效。本附录为纯流程记录，不改变受审实现与本报告结论。

## 附录 B：报告事实澄清与勘误（2026-10-20，第二轮追加）

派发方对本报告提出事实澄清（来源快照 `zcode-runtime/factual-clarification-source.json`）。原 139 行初稿已按原字节保存于 `zcode-runtime/report-before-factual-clarification.md`，SHA-256 `834f5c717f9a7db48e494b162b7679d5360b45b63d8d108e77fdfca2ccb50bc6`，经我实算一致；附录 A 的追加差异另存于该目录。本轮仅勘误本报告，未改实现、未重跑不变的 full check、未打开另一模型报告内容、未运行任何窗口。全部勘误均以 `git show f574a7234923f28e9356a45a17253803e7602e06` 读取固定候选重验，未机械替换：

| 原稿表述 | 核验事实 | 处置 |
| --- | --- | --- |
| errors 24 码 / schema error.oneOf 24 分支 | 实为 **26/26**（`git show f574` 逐项重数；逐字段一致性结论不变，仅计数笔误） | §3 已更正并注勘误来源 |
| registry 19 项 | 实为 **24 项**（14 服务方法 + 10 job 能力；$ref 全部可解析的结论不变） | §3 已更正 |
| "inputs/sources.json 12 项 SHA 由测试锁定" | inputs/sources.json 实为 **6 份冻结输入**；`verify:sources` 的 12 项是 `docs/source-manifest.json` 归档源清单，两者不同源 | §4 已拆分表述；两项校验本身均实跑通过 |
| "截至本报告完成时 round-1 目录亦不存在另一报告" | 不符合文件历史（勘误时 `ls` 显示另一报告已于本轮中途存在）；存在性非我可回溯证明的事实 | §1 改为仅陈述未读取/未使用其内容，不再断言存在性 |
| R6"已关闭（延期保留）" | I01 round-3 处理记录原文为"R6 历史增长留真实负载/Q5 目标后设计"，属开放延期项 | §6 改为"承接说明已记录（契约层），原问题保持 I01 登记的开放/延期状态与原等级，不构成关闭" |
| 隐含"报告文本经过 prettier 格式校验" | `--file-info` 显示报告位于 `.prettierignore` 的 `docs/reviews` 下（`ignored:true`、`inferredParser:null`）；退出 0 源于忽略 | 附录 A 已区分"命令退出 0"与"内容被格式校验"，明示报告文本未经 prettier 内容检查 |
| 任务来源表述 | 需区分"总控核验人类授权并预约"与"I03 派发会话经 CUA 实际创建任务并读回"；account 标识为任务环境自报标签 | §1 已分层改写，status.md 引用改为真实标题「候选4外审实际创建与控制中断（仅流程追加）」（45–49 行） |

其余数字经 `git show f574` 独立复验无误，未改动：fixtures cases 314 / responses 30 / validationBindings 20 / routing 11 / cursors 9 / jobListCursors 7、变更文件 37 份、TS 420（5 文件，其中 contract-v2 405）/ Python 622、UNSUPPORTED_CONSTRUCT 17 枚举、RESOURCE_LIMIT 8 枚举、依赖策略 7 项。

**结论重申（独立重估，非默认维持）**：上述勘误全部属于报告事实表述精度问题——被误记的计数背后，集合相等性、引用可解析、哈希锁定等实质校验当时均已真实通过；R6 重分类还原的是 I01 原始开放状态，其本身从来不是 I03 退出门槛；prettier 与任务来源两项只影响流程记录口径。逐项重估后，没有任何一项动摇 §4 验收核对、§5 问题清单（3 项 P3 + 4 条观察）或 §7 证据边界的实质判断。最终结论仍为**通过**，原失败/未验边界全部保留不变。本附录为纯流程勘误，不改变受审实现。
