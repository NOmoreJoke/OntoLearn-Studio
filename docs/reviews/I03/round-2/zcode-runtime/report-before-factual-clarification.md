# I03 Round 2 独立对抗性审查报告（ZCode / GLM-5.3）

## 1 任务、模型及思考设置的来源记录

- 任务标识：`I03-R2-ZCode-GLM53-C5-30c10d8`（派发相关 ID，非原生 UUID，本环境未提供原生 task UUID，如实注明）。来源分层：总控核验人类授权并预约；I03 派发会话经原生文件夹选择器在精确 worktree 实际创建本任务并读回 GLM-5.3/最高（派发方声明，见 `round-2/tasks.json`）；本任务环境自报模型标识 `account:bigmodel-individual-coding-plan/GLM-5.3`、思考最高，属任务环境自报标签，任务内部无法独立核验 UI 读回结果，两者分开记录。
- 独立性：本报告对 base→head 全范围独立重审，未读取、未使用另一模型（M3.1-Flash/xhigh）round-2 的报告、运行输出或本轮意见，也不以其结论为依据；本轮允许对等读取的 round-1 历史材料（含对方 round-1 报告原稿与勘误）已实读，仅作历史事实输入，不影响本轮独立判断。未因任何历史通过预设本候选通过。
- 操作约束遵守：仅纯 CLI 验证（typecheck/check/verify:sources/pytest/tsc/vitest 探针）；未运行 Electron/Playwright/e2e/native/HMR/产物窗口，未点击/聚焦/重建任何窗口；未提交/推送/切分支；候选工作树零写入（`git status` 验证前后一致）；仓库内仅写入本报告与 `round-2/zcode-runtime/` 日志；未替换模型/思考/账号，未购买/重置额度。
- 资源边界（重要，按派发约定记录）：本轮首段独占本 worktree 共享 build/out，在该窗口完成 `npm run typecheck`、`npm run verify:sources` 与完整 `npm run check`（含 electron-vite build）；check 退出（exit 0）后我**立即在会话中明确通知派发方释放共享构建资源**，总控随后确认预约已转交另一任务。此后全部工作为固定源码只读检查与自有 /tmp 阶段：类型注入与漂移探针在 `/tmp/i03-r2-zcode/inject`（`git archive HEAD` 副本 + node_modules 只读符号链接）进行，Python 探针 `uv run` 只读源码、临时 SQLite 仅在 /tmp，TS 探针用 /tmp vitest 配置挂仓库源运行——均不读取也不写入任何共享构建输出。

## 2 项目路径、分支、base 与 head（实际核验）

| 项 | 值 |
| --- | --- |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I03-protocol-contracts`（`git rev-parse --show-toplevel` 实测） |
| 分支 | `feature/I03-protocol-contracts`（`git branch --show-current`） |
| base | `c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3`（实测存在且为 HEAD 祖先） |
| head | `30c10d8ad1b9156b1fa5317c6b41b179f927c761`（`git rev-parse HEAD` 一致） |
| 提交序列 | ad9756e → 6f35ffd → 8305d20 → 0ec24b7（merge origin/develop，含 I02 基线）→ f574a72 → **30c10d8（候选5修订：close review findings and enforce strict type gates）** |
| 变更规模 | 101 文件，+26214/−11（其中 30c10d8 本身 +4576/−68；代码改动集中在 9 个文件，其余为评审材料归档） |
| 受保护 AGENTS.md | 工作树 SHA-256 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786` 实测与保护声明一致；dirty 未 stage、未混入任何提交（candidate.json `featureCommitIncludesFile:false` 亦记录） |
| 其他 dirty | `docs/reviews/I03/status.md` 为总控纯流程追加（候选5第二轮任务创建记录，diff 实读核实只含流程段落），不属于受审实现；未跟踪的 candidate.json/frozen-integrity.json/blocked-audit.json/round-2/ 为流程件 |
| push/PR/CI/合并 | 均未发生（candidate.json 记录与本地状态一致） |

## 3 实际执行的验证（原始退出码与完整日志在 round-2/zcode-runtime/，镜像于 /tmp/i03-r2-zcode/）

| 命令/探针 | 退出码 | 结果 |
| --- | --- | --- |
| `npm run typecheck`（根，三段：contracts strict → unit strict → desktop） | **0** | stdout 实证三段依次执行；stderr 空 |
| `npm run verify:sources` | **0** | 12 个归档源文件一致 |
| `npm run check`（lint→format→typecheck→vitest→build→ruff/pytest） | **0** | vitest 5 文件 **424/424**；electron-vite 三段构建成功；ruff 通过；pytest **626 passed**；stderr 空。与冻结证据声明（424/626）一致 |
| `git diff --check c2f9b038..HEAD`（未过滤） | 2 | 全部 48 处空白错误**仅在**两份历史统一 diff 审计工件（typecheck-clarification.diff / factual-clarification.diff）的空上下文行，属逐字保留产物 |
| 同上，排除 `docs/reviews/I03/**/*.diff` | **0** | 实际源码/配置/测试/文档无空白错误；排除范围经我逐条核对确属 .diff 工件，未借排除掩盖实现问题 |
| 类型注入（/tmp 副本）：contracts 源码注入真实 TS2322 → `npm run typecheck` | **2** | `src/states-v2.ts(20,14): error TS2322`；git archive 恢复后 exit 0 |
| 类型注入：unit 测试注入真实 TS2322 → `npm run typecheck` | **2** | `tests/unit/contract-v2.test.ts(273,37): error TS2322`；恢复后 SHA `96d196c4…` 与候选逐字节一致，exit 0 |
| SQLite 守卫探针（真实库，自写 7 断言组） | **0** | **7/7**：results 与 current_results 既存 NULL kind 开库拒绝且 iterdump 逐字节不变；publish 对 7 种非法 kind/7 种残缺 provenance 全部 ValueError 且零写入；current 形状错误与合法未找到 null 区分；同合法身份恰好一条 current；legacy 非对象 config `Run config must be an object` 且 progress/rounds 零副作用 |
| Python 对抗探针（自写 24 断言） | **0** | **24/24**：F2 旧键双拒/新键双收/非空 params 拒/错误 retryable 拒；F4 预算缩至 1 拒、恢复后收；版本三元一致；cancelling→succeeded 证明门；终态倒退/同版本拒；通知 seq 缺口/重放/错订阅/版本跳变拒；游标到期/页大小变更/伪造 token/绑定失配拒 |
| TS 对抗探针（vitest /tmp 配置挂仓库源，20 断言） | **0** | **20/20**：与 Python 侧同批断言完全一致（含 hello capabilities⊆v2Runtime=[] 拒绝） |
| F1 漂移注入（/tmp 副本删 `TIMEOUT.heartbeat` 含义） | **1** | 仓内动态穷举测试**真实失败**（1 failed/408 skipped）；errors.json 恢复后 SHA `6986be7c…` 与候选一致。Python 侧同漂移以 AssertionError 检出 |
| Z 漂移注入（/tmp 副本删 `params_hello.supportedVersions.maxItems`） | **1** | 词汇/上界元测试**真实失败**；schema.json 恢复后 SHA `adc99635…` 与候选一致 |
| 哈希核验 | — | 两份 I05 交接快照 SHA-256（`ad84c439…`/`ea40f827…`）与 `I05-contract-source.json` 声明一致；注入证据 `typecheck-gate.json` 的 original/restored SHA 与当前工作树实测一致 |

过程披露（保留失败与修正，不改写为成功）：SQLite 探针首版用错 API 签名（1/6 通过）→ 读真实签名后重写为 7/7；Python 探针游标正例首版缺 `lastOrdinal/lastRowId`（23/24，负例当时不可信）→ 改用仓内 `valid cursor` 夹具为基底后 24/24；TS 探针配置首版导入 `vitest/config` 在 /tmp 不可解析 → 改纯对象默认导出后通过；errors.json 结构我初读时误将枚举值键当参数名 → 读原始 JSON 修正。全部原始输出保留于 `round-2/zcode-runtime/`，探针源码在 `/tmp/i03-r2-zcode/probes/`。

## 4 候选5重点修订项逐项复核（独立证据，非引用开发方声明）

| 项 | 复核结论 | 独立证据 |
| --- | --- | --- |
| **F1** parameterMeanings 全覆盖+动态穷举 | **成立** | 我程序化比对：7 个含枚举参数错误码（INVALID_REQUEST.field/NOT_FOUND.resource/TIMEOUT.phase/MAPPING_VALUE_INVALID.field/SEMANTIC_INPUT_INVALID.field/UNSUPPORTED_CONSTRUCT.construct/RESOURCE_LIMIT.resource）的枚举值与 meanings 键**逐值精确相等**（7/7/6/4/4/17/8），无空含义、无多余码、每码恰一个枚举参数；TS 测试 192–211 行与 Python `test_all_enum_parameter_descriptions_are_complete` 均为遍历式动态断言（非硬编码两码）；漂移注入实测两端的检测真实生效（§3） |
| **F2** 通用 messageKey+旧键负例 | **成立** | errors.json 与 schema.json error oneOf 分支同步为 `resource.limitExceeded`/`protocol.invalidState`（const+required 实证）；fixtures 含 `reject retired messageKey job.resourceLimit`/`job.invalidState` 两个专属负例（valid=false）及新键正负例（26/3 处命中）；protocol.md:70 明确"由固定 resource 参数区分产生者、不从模板命名空间推断"；错误码总数不变（26/26，schema oneOf 与 errors.codes 逐字段一致由仓内测试锁定且我比对成立） |
| **F3** 标准根 typecheck 严格三覆盖+真实注入 | **成立** | 根 `typecheck` = contracts strict → `tsc -p tsconfig.unit.json`（extends contracts strict、types:node、include `tests/unit/**/*.ts`，`--listFiles` 实证 5 个单测文件全部入程序）→ desktop；CI 两处入口（ci.yml:30 `npm run check`、:69 `npm run typecheck`）均直接消费该入口，无 CI/依赖/锁改动；旧 TS2698 两处以 `objectValue/objectFixture` unknown→对象收窄修复（18–27 行），无 any/`@ts-ignore`/eslint-disable（grep 实证）；我在 /tmp 副本独立注入两处真实 TS2322，标准入口均 exit 2，字节恢复后 exit 0，恢复 SHA 与候选及 typecheck-gate.json 三方一致 |
| **F4** 两端动态消费同一预算/版本 | **成立** | `v2.ts:160` 与 `contract_v2.py:131` 均改为读 `ERROR_CATALOG.maxEncodedBytes`（grep 确认无第二份 2048 硬编码残留于校验路径）；两侧运行时缩小预算→拒绝、恢复→接受的测试真实存在且我的独立探针两端复现；版本一致性（errors.schemaVersion == registry.schemaVersion == schema `$id urn:ontolearn:contracts:2`）测试+我的独立断言均通过 |
| **F6** E.2/FR701/FR704/G.4 场景终态摘要 | **设计闭环** | jobs-and-storage.md §运行结束与未处理事件（30c10d8 新增）：`job.succeeded`≠事件耗尽；`run.summary.v1` 八格固定布局沿 `job.resultRef→result.get→result.page` 承载，**无新增业务方法**；成功摘要 `lastCommittedRound≥1`、零提交失败/取消仅状态与 `committedProgress=null`、不生成成功摘要；`hasUnprocessedEvents≡count>0`；摘要只在首个非游标页出现；**未选择的提前停止规则不添加**。I03 只冻结布局，通用 row 校验器不声称摘要生成/引用真实/业务解码——与范围边界一致。内审发现的"零轮成功摘要与 succeeded≥已提交轮冲突"已修正并有记录 |
| **Z** 双端词汇/数组显式有限上界元守卫 | **成立** | TS 测试 235–271 与 Python `test_canonical_schema_vocabulary_and_explicit_array_bounds` 遍历全部 `$defs`：未知词汇拒绝、`type:array` 必须显式 `maxItems`（安全整数≥0 且有 items）；两侧词汇表我提取比对**逐词相同**（19 词）；漂移注入实测元测试真实失败。schema 当前状态：未知词汇 0、全部数组显式上界（round-1 已验，本候选 schema 仅改两处 messageKey const） |
| **kind** 显式白名单/拒绝未知 | **文档闭环（实现属 I04）** | jobs-and-storage.md:83：内部 kind 仍按既有非空字符串身份保存；I04 公开映射"须显式白名单映射或拒绝未知值；不 trim、大小写归并或合并既存身份"；全库 legacy-kind 扫描保留；**I01 R6 保持原级开放/延期**，无测量依据的扫描优化不实施——与派发指示逐条一致。S1 侧现状由我的 SQLite 探针复证（非空守卫+零清理+唯一 current） |
| **I05 语义交接完整** | **成立** | v3 表 25 行与源快照**逐行码序完全相同**（程序化比对）；五个退休合码（INPUT_LIMIT/RESULT_LIMIT/UNSUPPORTED_LITERAL/UNSUPPORTED_RDF/ASSERTED_SCOPE_REQUIRED）在 v3 表与来源分支 0 命中、仅存历史表；SHAPE_PATH_UNCLASSIFIED 仅 INTERNAL_ERROR/{}；两份快照 SHA 一致；semanticInput/Result/Work 与 frame/page/行为预算分开（protocol.md:58 + meanings 文案）；来源归责三分（用户输入/可信违约/无法分类）逐行保留；validationResources 可信绑定 20 夹具未变；不采纳 Q6、不把 I05 检查点当已接入（文档原文核实） |

其余结构核验：registry 24 能力全部 design-only(21)/test-design-only(3)，`v2Runtime=[]`、`productRuntime=["health"]`；dependencies 7 策略与 registry 一一对应无孤儿；states.json 转移表与文档状态机逐边一致；fixtures 语料连续性——候选4 的 314/30/11/9/7/2/20/2/2 条用例名**全部保留**，净增 2 条旧键负例（316 cases）；14 个方法信封正例+未知方法/未知参数负例覆盖完整（'eval' 即未知方法负例）；v1 health 路径（`packages/contracts/src/index.ts`）、apps/desktop、引擎 `__main__.py`/`protocol.py` 在全范围**零改动**。

## 5 acceptance.md「I03 必须通过」逐行判断

| 验收行 | 判断 | 依据摘要 |
| --- | --- | --- |
| 信封与每方法严格 | 通过 | 每方法 params/result `$ref` 可解析；399 条夹具双端一致重放（424 测试含 399 夹具驱动）；unknown method/extra params 反例实测拒绝 |
| hello、身份与响应绑定 | 通过（设计层） | bootstrap/无交集[2]/二次 hello INVALID_STATE/握手前 HANDSHAKE_REQUIRED 在 schema 与文档；matchesResponse 绑定 id/method/session/project/job/nonce/operation/subscription；hello capabilities⊆v2Runtime=[] 我实测拒绝；常驻握手属 I04 |
| 安全错误 | 通过 | 全码正反例跨端语料；五参数、2048 字节预算（现为目录驱动）、受限引用；固定错误码/无自由文本/无堆栈路径原值（探针复证）；分层语义文档互斥 |
| 取消与状态 | 通过 | states.json 转移表与文档一致；cancelling→succeeded 需 finalBeforeCancel 证明门（我两端探针复证含 false 拒绝）；零轮 null/两轮保留/非轮次拒绝在 commitProgress 分支 |
| 真实依赖 | 通过 | 7 策略与九能力表一致；deriveDependencies 环去重/悬空拒绝/4096 上界（夹具+round-1 差分，本轮结构未变）；model 可跟踪不产生领域码 |
| U1 | 通过 | 身份表/current 指针/草稿边界完整；result current/stale/historical+payloadStatus=evicted；result.page 完整 binding+服务端 cursorRecord+CURSOR_MISMATCH/EXPIRED/PAYLOAD_EVICTED；job.list 双身份不可变列表快照+稳定序 |
| S1 实际边界 | 通过 | 我的真实 SQLite 探针 7/7：NULL/空 kind 开库拒绝零清理（两表）、非法 kind/provenance 零写入、合法身份唯一 current、legacy config ValueError 零副作用 |
| S1 交接无遗漏 | 通过 | jobs-and-storage「I01 交接闭环」11 项与 I01 round-3 处理记录逐条对上（含 F3-05 固定顺序、F3-04 恢复语义、锁/I/O 主码映射、N-06 幂等） |
| 独立审查与源输入 | 通过 | inputs/sources.json 6 份冻结输入 SHA 由测试锁定且 verify:sources 12 项我实跑通过；内审 A/B/C+候选5 各系列有关闭记录；本报告为指定双外审之一，另一模型独立进行 |
| 仓库静态与引擎回归 | 通过 | typecheck（三段）/check（424/626）/verify:sources/diff --check（按注明的 .diff 排除）全过；未启动任何窗口 |

## 6 问题清单

**未发现 P0/P1/P2 问题。** 以下为本轮新记录的 P3 级残留/观察，均不阻断：

### O1（P3·残留，承接 Z P3-1 的部分采纳处置）词汇/上界之外的不可达双端分歧模式仍在代码中

- 位置：`packages/contracts/src/v2.ts:46-48,73,115`（未知词汇 `fail()` 抛异常且 `validateV2` 不捕获 vs Python `check()` 返回 False；数组缺 maxItems 时 TS 默认 100000 vs Python 无上限）；另有 4 处子集 vs 全等比较（`semantic` 投影 implementation、`matchesResponse` job.create input 与 result.page binding、`cursorMatches` binding、`validationProjectionMatchesResources` implementation）。
- 触发：仅当未来 schema 演进引入新词汇、省略数组上界或放宽相关对象键集时可达。当前 schema 未知词汇 0、全部数组显式上界、相关对象为固定键集 strict，分歧不可达，且本轮已实测词汇/上界两条不变量的元测试在漂移下真实失败。
- 影响：双端"同一公共样例接受/拒绝完全一致"的 I04 前提在当前候选成立；风险仅在未来 schema 变更未先统一适配器失败行为时显现。
- 建议：I04 扩展 schema（新词汇/可选键/默认上界任一）前，先统一双端失败模式与比较口径并复审——processing.md 已把该前置条件写入处置，属已登记延期，无需本轮行动。

### O2（P3·观察）parameterMeanings 含义为单语英文散文

53 条含义均为英文固定句子，作为**语义目录**（非显示文案）自洽且与枚举精确对应；UI 四段式文案与本地化映射属 I04 的 messageKey→文案层，不该也不会直接复用这些字符串。无行动要求，记录以供 I04 不误将其当 UI 文案。

### O3（P3·观察，与 Z P3-2/F7 同源）开库全库 legacy-kind 扫描成本保留

无测量依据不实施优化，扫描保留；I01 R6 历史增长维持原级开放/延期，真实负载测量与修复政策由 I04/Q5 承接。与派发"不得把 R6 改关闭、无测量依据不优化"指示一致。

## 7 历史意见逐项处置判断（契约闭环与运行时完成分开）

| 历史项（round-1） | 本轮独立判断 | 依据 |
| --- | --- | --- |
| MM F1（P2 参数含义覆盖） | **契约闭环（本候选）**；UI 文案接入 I04 | §4 F1：7/7 精确对应+动态穷举+漂移实测检出 |
| MM F2（P2 模板命名误导） | **契约闭环（本候选）**；端到端传播 I04 | §4 F2：新键+旧键负例+文档判据 |
| MM F3（P2 类型门禁+TS2698） | **闭环（本候选）** | 三段严格覆盖+CI 消费同一入口+两处注入独立复现 exit2/TS2322/恢复 exit0；TS2698 已由 unknown 收窄消除 |
| MM F4（P3 预算/版本无消费者） | **闭环（本候选）** | 两端读目录常量+运行时缩小验证+版本三元一致 |
| MM F5（P3 source→public 映射仅 Markdown） | **延期 I04/I05（开放）** | 处置记录如此；25 条可信来源文档仍为规范，未凭空加第二份映射真相——合理延期 |
| MM F6（P3 未处理事件终态路径） | **设计闭环（本候选）**；摘要生成/分页解码/持久联验 I04（运行时开放） | §4 F6 |
| MM F7（P3 观察，已撤回性能缺陷） | 观察保留；扫描优化不实施 | 与 O3 合并记录 |
| MM F8（P3 观察 readOnlyViewPolicies） | 观察保留 | v2Runtime=[] 继续准确 |
| Z P3-1（双端 fallback 差异） | **部分采纳后闭环**：元测试锁两条不变量；fallback 行为统一延期（见 O1 残留） | 漂移注入实测守卫生效 |
| Z P3-2（开库两次全表扫描） | 延期 I04/Q5（开放） | 无测量依据不优化；拒绝损坏身份语义保留且我复证 |
| Z P3-3（kind 前后空白） | **文档级处置**：I04 白名单映射/拒绝未知、不 trim/归并；运行时开放 | jobs-and-storage.md:83 |
| Z 观察 1–4（接收/应用分层、cancel 快照、maxActionsPerRound=1000、historical 读 current） | 保留记录 | protocol.md:56 与 jobs-and-storage 相关文本未变 |
| I01 移交 11 项（N-R3-1/2、F3-02、F3-03…N-06） | 前三项**代码级关闭**（我的 SQLite 探针独立复证）；其余**契约级关闭**；实现/联验归 I04 | §5 S1 两行 |
| I01 R6 历史增长 | **保持 I01 登记的开放/延期原级，不构成关闭** | jobs-and-storage.md:83 原文如实保留；无存储优化混入 |

## 8 未验证事项与证据边界

- 常驻进程、真实 JSONL reader（拆包/粘包/UTF-8/重复键/追加前字节限额）、队列/worker/取消竞态、持久 job/marker 对账、窗口重连、Python→主进程→bridge→UI 错误全链路与四段式 UI、场景摘要实际生成与分页解码——**I04**，本候选未宣称完成。
- 真实 RDFS/pySHACL/分层图投影、C→Mid→Equipment 与 x 类型真实反例、外联拒绝与打包测量——**I05**；I05 源检查点 02a8c909 本线不可达，仅交接快照哈希与逐行表一致可证。
- Electron e2e/native/HMR/产物启动——本机禁止，留隔离环境；push/PR/远端 CI/合并/远端 develop 核验——门禁未到。
- 另一模型 round-2 报告——独立进行，未读。
- 证据边界：纯校验器接受已解码 JSON 值，不证明原始帧字节、marker 真实存在、hash 对应真实 blob、权限成立或引擎计算正确——候选文档对此如实声明，与本判断一致。校验器语义是"结构+跨字段一致性"，不是运行时完成。

## 9 最终结论

**通过。**

候选 5（base `c2f9b038…` → head `30c10d8…`）在 I03 冻结范围内满足全部可现实验收：round-1 全部 15 项意见中采纳项（F1/F2/F3/F4、F6 设计、Z 元守卫、kind 白名单要求）均以**我独立复现的证据**闭环，延期项（F5、F7/F8、P3-2、P3-3 运行部分、R6）保持开放且有明确归属；acceptance.md 十行全部通过；四类标准命令与 5 组自建对抗探针（SQLite 7/7、Python 24/24、TS 20/20、双漂移检出、双注入 exit2）独立全绿；夹具语料对候选 4 完全保留并净增 2 条旧键负例；v1 health 未动、`v2Runtime=[]` 诚实零声明；I05 v3 25 细码交接逐行一致、退休合码未回流、Q6 未采纳、R6 未被改关闭。本轮新发现仅 3 项 P3 观察/残留（O1 双端 fallback 残留属已登记延期、O2/O3 为观察），无阻断或重要问题，允许延期。

本通过不将任何 I04/I05 运行项、桌面联验或远端 CI 登记为完成，不改变 Q2/Q3/Q5–Q9 决策边界，不构成 push/PR/合并授权；处理方仍须按门禁汇总双方本轮意见并逐项记录处置。

——审查者：ZCode（GLM-5.3，思考最高），任务 I03-R2-ZCode-GLM53-C5-30c10d8，2026-10-20。原始日志与探针输出：`docs/reviews/I03/round-2/zcode-runtime/`（24 项）与 `/tmp/i03-r2-zcode/`。
