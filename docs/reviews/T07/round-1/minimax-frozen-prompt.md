# T07-S1 round-1 MiniMax Code 独立完整审查冻结正文

你是本轮独立审查者，必须使用M3.1-Flash，思考xhigh，权限permissionMode=bypassPermissions。负责人先实际读回任务级设置并保存证据，用户默认/界面模型名/进程ready不能代替。T07尚无租约，本文件不构成派发许可；取得当时有效租约和支持的官方入口后才可提交全文。当前T06独占后台恢复资源；T07自己的后台路线尚未核验。不得沿用旧C2或昨日GUI许可。

原工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-scenario`，分支 `feature/weekly-t07-scenario`。只读固定base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → 产品/测试head `f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3` 的完整25路径diff。过程parent `982e4535e864c17275e51ed67664c0b7fac367bc` 后本round-1仅流程材料，不能覆盖固定产品。未来隔离review checkout由负责人提供并记录真实绝对路径映射；核base祖先、完整diff及25路径/14项精确身份，不自行切分支。不一致时保留现场报告无法验证，不能修产品。

范围为“完整私有轮次编排/资源FIFO指标/独立场景页及现有验证”，涵盖全部25路径，不缩为投影/页面/测试补丁。独立找反例，不预设历史内审结论。不得读取另一指定模型本轮报告或接收其本轮意见；历史原始内审与问题仅用于历史关闭核验。

## 全部输入

先读本目录 README.md、frozen-manifest.json、archive-manifest.json、historical-issues.md、internal-review-sources.json与9条原始final。candidate.patch是完整binary/full-index diff，SHA `3e697c94bae835307e1012bb30ea65bbbce680555e488135bfcb267b4210b8a3`。frozen-inputs.tar.gz按manifest核验后只读，不执行其脚本；25路径全部读取：

- `apps/desktop/src/renderer/src/scenario/ScenarioPage.tsx`
- `apps/desktop/src/renderer/src/scenario/presentation.ts`
- `apps/desktop/src/renderer/src/scenario/scenario.css`
- `docs/iterations/T07/acceptance.md`
- `docs/iterations/T07/integration-request.md`
- `docs/iterations/T07/round-projection-handoff.md`
- `docs/reviews/T07/.gitignore`
- `docs/reviews/T07/evidence/candidate-files.json`
- `docs/reviews/T07/evidence/persistence-validation.json`
- `docs/reviews/T07/evidence/render-probe.mjs`
- `docs/reviews/T07/evidence/t09-input-receipt.json`
- `docs/reviews/T07/evidence/ui-probe.json`
- `docs/reviews/T07/evidence/validation.json`
- `docs/reviews/T07/internal-review.md`
- `docs/reviews/T07/status.md`
- `packages/engine/src/ontolearn_engine/scenario/__init__.py`
- `packages/engine/src/ontolearn_engine/scenario/model.py`
- `packages/engine/src/ontolearn_engine/scenario/runner.py`
- `packages/engine/tests/test_scenario_persistence.py`
- `packages/engine/tests/test_scenario_rounds.py`
- `tests/fixtures/scenario/e5.json`
- `tests/fixtures/scenario/round-projection-handoff.json`
- `tests/fixtures/scenario/t09-e5.json`
- `tests/fixtures/scenario/t09-manifest.json`
- `tests/unit/t07-scenario.test.ts`

14项实现/测试/fixture精确身份全部核验：

- `apps/desktop/src/renderer/src/scenario/ScenarioPage.tsx` SHA256 `65ac6a8efd6a9f395088403be8e0133cd1f32f3f70f34334e1f5a135f65c30ac`
- `apps/desktop/src/renderer/src/scenario/presentation.ts` SHA256 `3474e356ffc7dd9f3c5bddaea4ba9a1e6e6259020e9ee22dd2e9769d15a5e463`
- `apps/desktop/src/renderer/src/scenario/scenario.css` SHA256 `d3889694abc93c3bc3973f20a01c176187b927c5ce4a53cf84d21108d74807b3`
- `docs/reviews/T07/evidence/render-probe.mjs` SHA256 `259c46a35de4f0edcf3be260c24d9df8a9554e991a91ba02df8c781333cdc308`
- `packages/engine/src/ontolearn_engine/scenario/__init__.py` SHA256 `6643227cd723fd3a1de0e41da31e634389d91ab7869863ef3736862cb7a31773`
- `packages/engine/src/ontolearn_engine/scenario/model.py` SHA256 `f30ce8d84b117805379933ce93025d9b0bcf61a3e8b0400feb0ad7ca4aa8f632`
- `packages/engine/src/ontolearn_engine/scenario/runner.py` SHA256 `69600dc9c9222b5102a75c261165bee309b4db0a72195b45de6915ff2104c702`
- `packages/engine/tests/test_scenario_persistence.py` SHA256 `0180923002708bad9d5e1806cfefc41616ae587d66fa34c9f44ec2ab75baf3e3`
- `packages/engine/tests/test_scenario_rounds.py` SHA256 `6038e0cd2d64c002dd9e6ec232afdeadb673663e6629f6e117a269d77785cc5c`
- `tests/fixtures/scenario/e5.json` SHA256 `84c299fa61de136965699a2b02c7b0c9cc7cde949abd86e8e68343c8a264e53b`
- `tests/fixtures/scenario/round-projection-handoff.json` SHA256 `924a5f2f8f3cc5d5777acea8f0e5da98937a7c466644303e1623e1b1ab34328e`
- `tests/fixtures/scenario/t09-e5.json` SHA256 `e81b0d02ac5f673552e1bd1e3e87206e7561e3c7fa9c658d5e0dbb41d426a5e5`
- `tests/fixtures/scenario/t09-manifest.json` SHA256 `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`
- `tests/unit/t07-scenario.test.ts` SHA256 `ce1ca32e272825fcf33bd5b38d78f371264c4e50ebba502cf3c13e1bf493a099`

批准规范按base固定读取PRD V0.6 FR-700–705、附录D、E.1–E.5、G.4/G.6、第10–12节；归档approved-reference含PRD、真实路径docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md、ADR-0001/0002。读取完整源码/diff、调用链、测试与fixture，不能用开发者摘要代替。T09只消费批准873c8c051b9870aa12fc7e1dbbd3e0c358e7c380原字节输入/17项hash，不采用其未批准服务。共享依赖仅以批准base为上下文；维护交接不批准实现/schema/runtime。

## 独立反例与证据判断

- 场景定义/来源/项目/引擎/依赖锁/规则行为参数身份、修改版本与历史隔离、复制和项目来源创建；V1晚到不得成为V2当前结果。
- 初始→事件→行为前推理→冻结计划/逐动作→FIFO→轮末推理/指标→单轮提交的严格顺序与Context(round,phase)；错阶段、轨迹身份/序号/重复/缺失、最大轮/动作1000、边界取消/失败、未来事件与去重、显式续跑一致性。
- FIFO创建轮/序号/ID与删除后不复用；三指标按实际集合；两产能/最大轮数/未来未处理全集。批准E5告警4/8/12/16，工单完成不消除告警；原私有零告警素材是独立合成例。
- 不可变历史；批准Store临时SQLite五事务边界×前轮0/1×异常/取消/真实READONLY，10个真实子进程退出、前轮保留/正式数据隔离、after_commit响应丢失对账。检查READONLY在runner外的严格异常类型/码名和禁用注入负对照；早期42项READONLY证明失效，不能因passed日志追认。
- 私有页面结构化输入、来源切换/资源模式/取消/历史依据/详情/比较逐轮最终值、缺轮、受限操作禁用与文本安全；合成headless回调不代替真实App/bridge/Store。
- 原始日志及首错/环境/候选/退出码证据；既有check657TS/1142Py，T07最后46+44Py/27TS。各次历史专项不能拼成同次运行；空ui-identity.log不独立证明成功。

必须保留未验项：真实T05初始/行为前/轮末推理，真实T06冻结条件/排序/冲突/动作；T01/I04正式scenario任务生命周期/取消/原子进度/终态/operation-id响应丢失对账；公共契约/bridge/App挂载；真实删除/恢复/快照创建/续跑；完整E5 facts/inferred/actionTrace/triggeredInstances、T10跨设备、FR-700–705及E.2–E.5/G.4/G.6父验收、macOS/Windows完整产品/平台/发布。S1可独立得出结论，不能借父缺口改小范围或虚称父验收已过。

## 只读职责与执行限制

只读固定源码/diff/证据；唯一允许写入为自己的报告 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-scenario/docs/reviews/T07/round-1/minimax-m31flash.md`。禁止改实现、测试、fixture、验收、依赖、配置、AGENTS、prompt/manifest；禁止git commit/push/切分支、安装产品依赖、第二套契约/Store写入通道。完全访问只是权限能力，不扩张职责。

先审已有完整证据，本次准备授权不包含新产品测试。确需验证时列具体命令/目的/隔离资源交负责人按有效任务/lease另行限定；不得自行运行npm lifecycle、GUI/Electron/e2e/native/HMR、产品启动、业务外联/模型、付费/重置或读取凭据。不得隐藏窗口/禁sandbox或hang monitor/stub冒充原生验收。只读文档/hash检查可执行并保留首错。不能更改用户默认模型、读取其他任务数据库或另一方本轮意见。

## 报告、真实终态与后续门

报告必须包括实际应用、task/session/turn ID、创建与正文受理时间、任务级模型/思考/权限读回及来源；真实源码/报告绝对路径映射、分支/base/head、diff/25路径/14项核验；完整所读范围、命令/退出码/首错/未运行项；每个问题的严重度、路径/行号、触发、影响、证据与修复建议；IR-01–05逐项关闭或重开；未验边界；明确“通过/不通过/无法验证”及依据。缺实际设置/完整读取时不能记Pass，缺证据照实写未知。

负责人须等真实任务终态、全文读回报告、封存原始final/来源/hash及冻结前后身份。文件存在/部分回复/进程结束/超时/取消/草稿都不是Pass。全部意见逐项处置，不能把你的不通过自行改成通过。产品/测试/配置/依赖/验收/base变化后新候选和双方各全新完整任务；不互传本轮意见。双方同版明确通过+必要验收+全部意见有处置后才可push/PR，实际CI成功后正常合并并核远端。本报告不关闭完整父Goal/平台/发布门。

## 最新操作政策全文透传

以下为准备时快照；执行负责人派发前重读当时最新政策。旧共同指令中的“必须CUA”“I05预约”已被10月22日后台规则修正；当前只有T06有lease，无新GUI授权。后台是待本任务核验的支持路线，不能将T06成功当T07入口已验。下文含完整原第九节、无桌面和默认权限约束；不创建替代Goal。最新版后台恢复快照在guidance/external-review-recovery-20261022.md及guidance/T06-supported-background-external-review-window.md，二者须一并全文读取。

### AGENTS.md（准备时完整快照）

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

### 本地验证默认不打扰用户（2026-10-20 用户确认）

- 本机默认只运行不打开窗口的静态检查、单元测试、引擎测试及构建/打包命令；打包完成不自动启动产物。上表的桌面 e2e 要求保留，但当前 `npm run test:e2e` 会启动 Electron，必须遵守本节的运行位置限制，不能作为本机每轮默认命令执行。
- 浏览器测试优先 headless；Electron 的原生窗口、可见性、焦点、无响应与恢复验收优先放在远程 CI、虚拟显示或独立测试桌面。`headless` 配置不能保证 Electron 无窗口；不得用隐藏/最小化窗口、禁用 hang monitor 或 stub 原生提示来冒充完整原生验收。
- 不得自动在用户当前桌面启动、显示、聚焦或反复重建测试窗口；禁止通过 `app.focus({ steal: true })`、`window.focus()`、`Raise`、自动点击或切应用占用用户正在使用的桌面。此约束也适用于 ZCode/MiniMax 等审查应用操作。必须使用当前桌面的验证，先汇总不可替代的待验项，等待用户明确提供可用测试时段；不能因用户未回复而自动重试。
- 无法静默完成的验证保留为“待隔离环境/桌面验证”，继续其余工作；不得记为通过、降低原验收或因等待擅自暂停/完成整个 Goal。既有证据仅在候选、环境和原验收范围匹配时引用，缺失部分在隔离环境补齐。
- 启动任务及派发独立审查时须一并传递本节约束；进行中任务在下一个安全边界停止新增本机 GUI 操作，撤回已排队的本机 e2e/native/HMR 桌面命令。有正在循环重建窗口的自有测试进程时，由所属开发线核对 PID、命令和任务归属后有界清理，记录中断而非通过；禁止宽泛结束 Electron、浏览器、审查应用或用户进程。

## 5. 分支、迭代与评审门禁

- **并行开发为默认执行要求（2026-10-20 用户确认）**：适用于当前 M0、后续里程碑、不同功能模块，以及单个模块内可独立开发的具体子任务。先识别真实接口、数据和集成依赖；可独立验收的工作须拆分并行推进，不得仅因迭代编号或模块顺序而全量串行。强依赖保留前置条件，不为增加并行数而重复实现或提前假定未冻结契约。
- **独立 worktree + feature 分支**：每条并行开发线使用自己的 Git worktree、feature 分支和负责 agent，禁止多个开发 agent 在同一 checkout 切分支或同时写文件。迭代使用 `feature/Ixx-<主题>`，模块子任务使用 `feature/<模块>-<子任务>`；其他改动使用 `feat/`、`fix/`、`docs/`、`chore/`。从核验过的 `develop` 提交切出并记录 base SHA，经 PR 合回；不强推共享分支。提交前缀使用 `feat:`、`fix:`、`docs:`、`test:`、`chore:`。
- **拆分与文件责任**：启动前记录各子任务的范围、前置依赖、接口约定、文件负责人、验收和集成顺序，再分配独立 agent。共享契约、存储迁移、能力注册表、依赖清单与锁文件指定唯一维护者；其他开发线提出接口需求，由维护者统一修改。依赖尚未就绪时，可先做独立设计、纯模块、真实库探针及对应测试，后置正式接线与联验；替身通过不得计作集成完成。
- **M0 的并行拆分**：I02 继续当前候选评审；I03 可基于已完成的 I01 并行设计；I05 可先做真实候选语义、外联拒绝、依赖与打包验证；I06 可先做网关 ADR、独立授权与凭据模块。I04 实施须等待 I03 同版本设计审查通过并合并；I05/I06 的正式接入及最终验收须等待各自实际依赖就绪，并补齐与存储、任务和窗口生命周期的联验。引入真实依赖时即做相应打包验证，不全部推迟到最终集成。
- **运行资源隔离**：各 worktree 独立依赖环境、构建输出、临时数据、日志及测试证据，开发端口和应用测试数据目录分别配置；不得共享可变运行库。桌面焦点、原生故障恢复、系统凭据存储及外部审查应用的 UI 操作由总控预约串行使用，避免运行互扰；已有固定端口或未隔离资源的测试须排队。
- **并行开发、按依赖串行集成**：每条开发线独立验证并履行现行评审门禁；合并前同步目标基线、处理冲突并验证实际集成结果。目标基线或受审内容变化时，按现行规则重新验证及独立审查，不沿用旧版本通过。保留双指定模型、CI 和远端核验要求；子任务完成不等于父模块或里程碑验收完成。
- **冻结与调度记录**：候选冻结后不得修改受审路径，任何实现、测试、配置、依赖或验收改动都要生成新候选，并按现行门禁重新独立审查。其他工作在独立 worktree 推进，不干扰冻结候选。总控记录并行任务、worktree/分支、base/head、文件责任、依赖和资源预约；仅按实际进展更新状态，不把获准并行登记为已启动或完成。
- **与旧计划的关系**：本节取代旧 `scope.md` 中“所有迭代必须前项合并后才启动后项”的统一串行调度要求；执行时总控须同步相关范围与调度记录，保留原需求、真实技术依赖、验收及评审门禁。后续功能模块和子任务同样执行本节，无需为常规并行拆分重复征求授权。
- **进行中开发与 Goal 的过渡**：无桌面打扰要求立即适用；并行策略在安全边界用于新任务/新开发线，不强行迁移正在冻结审查的 checkout、不改写其候选、不重建已有 Goal、不丢弃报告或重跑无变化的验证。用户授权的 AGENTS/调度文档变化单独记录前后哈希与适用范围；若未改变受审实现、测试、依赖、CI、验收或集成基线，不将其误判为受审产品变更，不单因此重开整轮审查。若实际受审内容或基线确有变化，仍执行原重新审查规则。审查代码读取固定 SHA，实际执行遵守最新操作约束。新 worktree 须携带并核对最新指南，不能只读取旧基线中的 AGENTS；总控负责同步规则，开发会话各自维护状态，避免共同改写 `state.json`。
- 不混入其他会话的未提交改动；禁止 `git add -A` 或整体 stage。只 stage 本任务文件。
- 复杂或高风险交付使用独立 agent 审查，避免并发修改共享契约文件；不得替换指定审查模型或降低门禁。

### 效率与额度恢复（2026-10-20 用户确认）

- 以正确交付和开发效率为优先，不因 token 消耗缩减实现、异常处理、上下文或必要验证。充分使用实际可用的并行 agent/worktree；避免重复探索、无变化重测和无效轮询，不擅自更换指定模型或降低审查门禁。
- 用户说明 ZCode、Codex、MiniMax Code 均有额外重置次数；遇实际额度限制时由账号唯一负责人核实状态，优先通过经核验的官方方式使用已有权益恢复，成功后续接原任务。其他开发线保存现场并继续无关工作，不重复消费同一权益；短时限速、服务/认证/账单故障不能当作额度耗尽盲目充值。
- 自动恢复受实际工具/平台约束：Codex `consume_usage_reset` 每次必须取得用户对该次操作的明确确认，未来批量授权不能替代；只在工具的额度条件满足时使用，同次不确定重试复用幂等 key，完成后核验额度，不因刷新失败重复消费。ZCode/MiniMax Code 的可用恢复机制尚待核实，不虚称已实现无人值守充值；禁止通过 UI 绕过工具确认或抢占用户桌面。
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
- 指定模型与思考等级、同版双审、意见处理、CI、远端核验及无桌面打扰约束继续适用；不扩大为新增付费、读取密钥、绕过平台逐次确认或占用用户工作桌面。
- 详见仓库外 `../iteration-control/2026-10-21-weekly-release/external-review-permissions.md`（worktree中从本体根目录定位）；新任务附上本节，旧冻结输入保留，单纯操作政策更新不触发无变化实现重审。

### developer-common-instructions.md（准备时完整快照）

# 完整首版功能开发共同指令

用户已在规划聊天 `01a15bad-ceeb-7103-b611-fff95e1f31ee` 明确要求 OntoLearn-Studio 全部原定首版功能于北京时间2026-10-25前开发上线、质量不降，并授权“发送并落实到现有总控”。总控实际读取原始用户消息确认了授权。本指令用于新功能开发聊天；截止日是目标，不是保质按期保证。

先读取本目录 controller-handoff.md、plan.md、tasks.json 中自己的任务、requirements.csv、acceptance-baselines.csv、review.md，以及实际工作树最新版AGENTS和对应PRD原条款/附录。57项P0、附录C–G及第10–12节保留；P1/P2原延期安排不变。T编号不覆盖I01–I06历史；纯服务完成不等于父模块P0完成，integration_prerequisites不是全部验收条件。

本会话只负责指定的一项功能，建立自己的Goal（不存在时），不继承总控Goal。先核验并回执绝对worktree、分支、base、实际git状态、指南SHA、唯一文件责任、验收与下一交付。总控已创建独立worktree，切勿改主checkout或其他树；AGENTS是总控复制的受保护操作规则，SHA应为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，保持未暂存，不混入产品提交。不得重建原I05/I06 Goal或继续写其树。

当前批准develop为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。I01–I04已合并；I05 C1在指定双审冻结，已发现词法语义阻断，I06在自己的14文件接线与隔离平台联验。不得采用未批准I05/I06实现、环境或测试结果为正式依赖。只读取已批准基线接口开展独立工作，具体接口缺口/共享改动向总控提供精确路径和依据。

初始共享责任（历史，已被下述逐项生效交接更新）：I06原独占 contracts/src/{index.ts,v2.ts}、contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json，desktop/main/{index.ts,task-service.ts,engine.ts}、preload/index.ts、renderer/src/{env.d.ts,App.tsx,style.css}；I05原保留其他Python Store/coordinator/worker/protocol、语义/resources、entrypoint/build/锁/CI/窗口安全恢复。这些逻辑文件在任何树中均不得抢写。新增私有路径可按本任务授权实施；现有共享文件、迁移和依赖锁一律先做具体交接。不得复制第二套公共契约、SQLite可变权威或Store写入通道来绕过交接。子任务独立worktree/feature和文件责任，复杂交付独立agent审查；核验真实并发槽，不将创建目录当作已启动agent。

后续责任变更补充：I05/T01双方实际接受、独立复核及总控登记后，只有 `packages/engine/src/ontolearn_engine/storage.py` 后续维护已交T01生效，详见 I05-T01-storage-ownership-handoff.md 和 execution-state.json。I05冻结树保持原字节，其余共享/14文件不变。不得将这个单文件交接扩张为其他文件授权；当前具体责任以总控实际生效记录为准。

2026-10-21新增已生效交接：T01除原storage.py外，已唯一接管Python四个 `packages/engine/src/ontolearn_engine/{job_store.py,coordinator.py,__main__.py}`、`packages/contracts/python/contract_v2.py`，及原I06 canonical七个 `packages/contracts/src/{index.ts,v2.ts}`、`packages/contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json` 和 `apps/desktop/src/main/engine.ts`，仅从批准5f独立实施格式基础。T03已唯一接管 `packages/engine/pyproject.toml`、`uv.lock`、`scripts/build-engine.mjs`、`packages/engine/entrypoint.py`，仅做XLSX最小依赖/收集/受限probe。原I05/I06树原字节保留，可读/构建但不得继续维护已交逻辑文件；必要修复先精确返还。I06仍维护其余六个main/index、task-service、preload/index、env.d.ts、App.tsx、style.css，I05仍维护其他未交路径；既有测试、CI、resources等不自动扩权。三份新handoff协议及独立报告/实际接受/生效通知见本目录 I05-T01-format3-ownership-handoff.md、I06-T01-format3-ownership-handoff.md、I05-T03-build-ownership-handoff.md 和execution-state.json；这不是未批准代码采用、公共格式启用或运行通过。

本机只允许无窗口静态、单测、Python、构建、unsigned目录打包；不得运行Electron/e2e/native/HMR、自动产物启动、抢焦点或凭据提示。原生可见/焦点/真实崩溃与无响应/实际安全存储在各自隔离Linux Docker/Xvfb/Openbox或远程CI准备；不关闭sandbox/hang monitor，不用隐藏窗口或stub原生提示冒充通过。Windows/macOS首发证据仍需实测；Linux不替代。ZCode/MiniMax审查应用当前资源预约属于I05，新线须先向总控预约，不自行抢用。CUA对Codex app已明确拒绝，禁止绕过。

开发至完整可审查结果，必要异常路径/事务/撤销/历史隔离均保留。AGENTS所需 check/sources/e2e/package 按实际改动执行，隔离项真实待验，首跑失败原件保留。文档/纯模块/静态检查不能冒充正式接线或生产。没有变化不重复测试。依赖资源缺失只阻塞相关部分，先完成独立工作，不擅自结束或暂停整个Goal。

最终完整验收前刷新实际批准依赖及develop、集成冲突并验证；冻结真实base/head。由同一开发聊天通过CUA在ZCode选择本精确工作树、GLM-5.3/最高，MiniMax Code选择本精确工作树、M3.1-Flash/xhigh；每轮双方各新建独立只读完整范围任务，不互传本轮意见。报告按 docs/reviews/Txx/round-N/{zcode-glm53,minimax-m31flash}.md，逐项含任务来源/模型设置/路径分支/base/head/检查命令结果/未验边界/问题严重度位置触发影响证据建议/历史逐项关闭/明确通过或不通过或无法验证。两个任务必须实际终态，全文读回、全部意见处置；不能自己把指定模型不通过改成通过。所有实现/测试/配置/依赖/验收或基线变化后重新验证并双方全新完整审查。纯追加流程证据记录对应关系，不自动触发无变化重审。

同版双方明确通过、验收和必要验证通过、全部意见有处置、实际推送内容与受审实现一致后才push/PR；实际CI通过后正常合并develop、核验远端与保护源。必须attach创建PR；无强推、绕过分支保护或双审前push。集成/外审按总控预约，减少前方候选基线失效。纯服务可单独冻结合并，但原父任务P0跨模块验收与完整发布门不关闭。

额度：效率和完整交付优先，不因token删减；真实告警由账号唯一负责人核实。Codex重置每次需本人明确确认/阈值/幂等，不能UI绕过；不新增付费、订阅、API消费或扩张授权。只读服务/身份元数据不含读取或输出密钥。真人非开发用户验收不能agent替代，向外招募/消息仍需用户明确授权。

各线只维护自己的 docs/reviews/Txx/status.md 及证据，不写根 state.json、tasks.json 或其他总控文件。及时保留可恢复SHA/原件和准确下一步；实际独立实现与验收证据成熟后向总控给出可读交付，不用反复询问常规实施许可。不能将配置/脚本存在、目录/模型名称或数量相同当作验收。完成后父模块/远端/上线分别据实记录。

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

### external-review-permissions.md（准备时完整快照）

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
5. 指定模型、思考等级、同版本双审、意见处理、CI 和远端核验继续保留。原无桌面打扰规则继续适用；本次未扩大为自动聚焦/点击用户工作桌面或允许原生弹窗。
6. 新任务提示词和共同开发指南附上本要求；历史冻结输入保留原样，文档权限规则更新本身不触发无变化的实现重审。

## 证据与接收

- ZCode 写前 SHA-256：`c7f88256c49fbae707d57bfcd294dfa4becee03169ded1f14f9ab7b8aa47bb5f`。
- ZCode 写后 SHA-256：`67f26b9702a009fa8353b77f9f9b6d44658bd9fc41f55b31e924d872cb2124`。
- 已逐项比较非权限配置及权限中其他字段，结构相同；未修改任务数据库、应用安装包、模型或思考设置。
- MiniMax 的本轮独立只读核验确认默认已符合；没有把静态文件核验当作每个运行会话的权限回执。
- 由现有执行总控维护调用指南与派发状态，在安全边界透传进行中开发线；实际发送/回执另行记录，不假定写文件即自动生效。

## 2026-10-22 后台恢复补充

已核验人类要求恢复指定双审并优先不打扰桌面的后台方式。支持的官方 CLI/app-server 可用于原开发会话创建、核验和监控任务；原指定模型、思考等级、逐任务权限读回、同版独立审查和全文终态门不变。原 T06 是当前唯一后台恢复 owner，其他线只提交现有固定候选就绪信息，不抢建任务。

昨日短时桌面答复确已回答，原先“未答复”记录有误，现已纠正；该时段不能沿用到今天。当前无新 GUI 许可，原 T06 已停止将旧答复当新许可的新增操作；MiniMax 草稿无正文/task ID，不计审查开始。具体固定输入、官方路线、错误和回执要求见本目录 `T06-supported-background-external-review-window.md`。不读取凭据、不新增付费、不私写任务数据库；协议进程启动、界面模型名或报告文件存在都不等于真实指定审查完成。
