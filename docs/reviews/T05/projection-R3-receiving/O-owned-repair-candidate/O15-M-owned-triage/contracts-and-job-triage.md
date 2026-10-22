# O15 M §8.1／§8.2：契约与 Job 隔离静态 triage

结论：§8.1 的“声明有边、JobStore 不执行该边”字面事实可证，但它尚不能证明“完整完成后迟到取消应保持成功”的实际时间语义失效；源码把完整结果与成功终态放在同一事务，迟到取消返回 `alreadyTerminal/succeeded`，已有直接强断言。两处通知消费者传 False 也有明确规范理由。§8.2 可证三份语料的消费测试没有固定预期 digest 门，但“只有 registry 被哈希”不准确：全部 v2 JSON 已纳入资源哈希与包／源一致性检查；registry 的 hash 本身也是动态计算值，并非独立固定金标准。尚无本轮运行反例、当前错误产品输入或“三套全部仍过”的变异复现。

两项仍为 `reported-open-awaiting-adjudication`，原 [中] 严重度、原 M 的 B150 NotPass、原15外部流程 open 全部保留。本报告不替 M 判 Pass，不将“边不可达”泛化为已证产品失效，也不将“存在同改风险”泛化为已发生权威基线漂移。

## 固定对象与只读边界

- 唯一源码 ref：`b88be226501703f1d5365734dd0e56066bd1bffb`。受审 process：`0f87f2c2a1fe5b8085176b530e473a7d51cea509`；process 不替代 source。
- 源码、规则与同 scope 测试均通过 `git show b88be226…:<path>` 读取。下列行号全部指该固定 ref，不借当前工作区源码推断固定候选。
- 派工：`docs/reviews/T05/projection-R3-receiving/O-owned-repair-candidate/O15-M-owned-triage/triage-assignment.md`。原稿只核读 §8.1 L363–370、§8.2 L371–378 及二者相邻 scope 声明。原稿为 `new-pair-minimax-terminal-intake/minimax-report-original.md.raw`，本次字节读取核得 59291 B、548 行、SHA-256 `256f7af033f4141bea9b26cc0895272e39076beeec1f39f69eda2b52ce6f2ada`，与分工记录一致；没有读取其余未知 metadata 或其他新外部报告。
- 未运行产品、pytest、oracle、observe、GUI、安装、网络或模型。没有构造或执行变异测试，以下因果分析均标为 static；提及已有测试，只表示固定源码内存在该断言，不声称本轮已通过。
- 唯一可写及实际新增文件为本报告；未修改契约、Job/storage、源码、测试、配置、其他 triage 或共享状态。共有契约／Job／storage 的裁决和实施交 root/T01 唯一 owner，本子线无修源权。

以下是从固定 Git 原件计算的关键身份，供复核定位；不是新运行探针。

| 固定 source 内路径                                  |   字节 | SHA-256                                                            |
| --------------------------------------------------- | -----: | ------------------------------------------------------------------ |
| `packages/contracts/v2/states.json`                 |    716 | `ab54cac024f0f6b31a8a229198ae1c4ab13f63ff88184cdcef78113b9e893416` |
| `packages/contracts/src/states-v2.ts`               |    578 | `cb82e8e5a047c875c93c4807b8a5f32f4174584d6d2e7b06b17d0f9f0e02b601` |
| `packages/contracts/python/contract_v2.py`          |  20174 | `0dc96a67cc47a03843a783cc47e649f13d5b5b80a43d520d0f6963b408d274fe` |
| `packages/engine/src/ontolearn_engine/job_store.py` |  64853 | `42cd05b91f03f4ec9d4d38d49e621094d0246b8b898385032d7c3005a0afd4f2` |
| `packages/engine/src/ontolearn_engine/storage.py`   |  55364 | `4abf1082f1b864eb9efa155c7cbc890ef70cb196f30e09ad12629ce7a0cf6842` |
| `packages/engine/src/ontolearn_engine/resources.py` |   2415 | `8bba36a3f97eedf972b4d9165e71b8046b225948b0864542a1fc3f1095c6f188` |
| `scripts/verify-i04-package.py`                     |   3290 | `fa0d5d6e134bd0205b1c9bc65bfa6a12aa45e56144d3b3745fe7028b45fb7ef1` |
| `packages/contracts/v2/fixtures.json`               | 472098 | `32031804abf3283e87f070ffbfc3f95cf627f6b71e7bc49711faaff52ec31ad6` |
| `packages/contracts/v2/binding-regressions.json`    | 123964 | `9601d6d0a31e3e71078ac2562c6b8501c1292bc2be71de742e40c2fc54512a24` |
| `packages/contracts/v2/frame-fixtures.json`         |  17537 | `8e9a142ff04e908cc286c15702cd18b6c2ce9453490585d0855c3f62995dd2e5` |

## §8.1：声明边、可达调用与时间语义

### 实际需求依据

1. `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md:93-105` 声明状态草案及取消竞态：`cancelling → succeeded` 仅用于完整最终提交／终态先持久化、取消后到；部分轮次不足以成功，已提交结果不能因取消被隐藏。
2. `docs/iterations/I03/jobs-and-storage.md:19-32` 保留相同边及前提，同时明确“已终态取消只返回已有证据，不是新状态边”；`:38-46` 又明确完整最终提交＋终态先持久化之后，取消应返回 `alreadyTerminal`、原 `succeeded` 不倒退。原规则既有抽象边，也有实际已终态幂等处置，不能只取前者。
3. `docs/iterations/I03/acceptance.md:12,28,31` 分别要求全状态纯契约证明门、最终提交后取消，以及 job／marker／round 同库事务；`docs/iterations/I04/acceptance.md:12,18` 要求完成后取消、最后轮没有终态不能成功、完整终态后取消不倒退。
4. `docs/iterations/I03/protocol.md:56` 明确：通知不能自证 `cancelling → succeeded` 的持久完成前提，必须先经 `job.get/operation.get` 对账；纯路由不能仅凭通知推断该竞态成立。这直接约束原报告提及的两处通知消费调用。

### 机械事实（static）

- `packages/contracts/v2/states.json:7,13` 宣布条件边，并要求全任务结果／提交和终态证据在取消线性化前已经持久化。
- TS `packages/contracts/src/states-v2.ts:2-17` 与 Python `packages/contracts/python/contract_v2.py:422-434` 都允许该边当且仅当调用者提供最终证据前置布尔值。纯值函数自身并不查询数据库，True 不是其自行验证的持久证明。
- 固定源码定向检索得到三个非测试消费点：JobStore `job_store.py:620-624`、Python 通知消费 `contract_v2.py:312-314`、TS 通知消费 `packages/contracts/src/v2.ts:360-368`，均传 False。原报告此字面事实成立。
- JobStore 三条成功路径在尝试 `_transition` 之前还各自要求 `running`：`commit_job` 的 `job_store.py:716-722,751-754`，`finish_read_job` 的 `:756-766`，`finish_job_run` 的 `:850-858,893,921-924`。因此现有正常持久 Job 路径不能用 `_transition` 产生 `cancelling → succeeded`；并非只把 False 换 True 就能使它可达。
- `_transition` 在成功时与结果指针一起 `_save`（`job_store.py:620-634`）；上述完整成功操作各在外层事务内。`JobStore._application` 在 `job_store.py:94-98` 组合 Store 事务；`storage.py:75-101` 规定嵌套 savepoint 仅外层 COMMIT 发布，异常回滚，提交后 hook 不能倒退已经持久的事实。
- `cancel_job` 在自己的事务内读取权威 Job：`job_store.py:640-661`；终态分支只返回 `alreadyTerminal`，未终态 running 才持久为 cancelling。`reconcile_jobs` 在 `:926-943` 保留终态，非终态不会仅凭 marker 发明成功。
- 协调器 `coordinator.py:271-282` 返回取消的精确线性化快照；`:523-542` 在最终提交前再次拒绝 cancelling，并走上述三条成功操作；`:544-557` 按持久状态收尾取消。不能拿 worker 计算结束、若干轮提交或 UI 点击时间替代 SQLite 的完成／取消线性化顺序。

### 两个次序的推演（static，未复现）

| 线性化顺序                                      | 固定实现的可达行为                                                      | 对原时间语义的含义                                                              |
| ----------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 完整结果＋成功终态外层 COMMIT 先，cancel 事务后 | cancel 读到 succeeded，返回 alreadyTerminal；原结果和终态不变           | 实现了“已经完整完成就不能倒退”的实际结果；不需要再写一次 cancelling→succeeded。 |
| cancel 持久化 cancelling 先，完整成功事务后     | 三成功入口的 running 守卫拒绝；随后按取消／失败收尾；部分轮次可保留历史 | 符合“部分提交不足以成功”；此时不能真实声称“完整终态先于取消持久化”。            |

在当前同事务表示下，“完整成功终态已经持久化，但当前权威 Job 仍为 cancelling”不是以上正常服务序列能产生的状态。要证明 §8.1 的产品损害，供方须指出具体可达序列：实际最终结果／终态已先 COMMIT，随后取消却使其丢失、回退或返回错误终态；或者证明现行需求明确要求即使采用原子终态表示也必须持久产生这条边。本轮未找到前一种反例；抽象契约与实现子集如何表达仍须 owner 裁决。

两处通知传 False 与规范 `protocol.md:56` 一致，不能与数据库成功路径混为“三处都缺实现”。如果未来通知端需要接受这条跨观察状态的边，应由权威查询核对完整 Job 后应用；不能简单把通知消费的 False 换 True。

### 已有强断言及其边界（仅静态存在）

- `packages/engine/tests/test_contract_v2.py:39-58`、`tests/unit/contract-v2.test.ts:152-169` 是明确完整枚举的纯状态矩阵：True 时枚举条件边，False 时拒绝，终态不倒退。这证明纯谓词的定义，不证明 JobStore 会传 True。把纯函数的合法 True 测试本身称作“产品永不调用所以测试无效”缺少层次区分；但它也不能替代 JobStore 可达行为验证。
- `packages/engine/tests/test_i04_round_faults.py:240-259` 先确认最后轮后仍 running、无结果、无 run terminal，再完整 finish，之后 cancel，精确断言 `alreadyTerminal/succeeded`、完整 Job 相等、完整 history 相等及终态 succeeded。此断言直接覆盖原要求的“最终完成后取消不倒退”，不是只数条目。
- `packages/engine/tests/test_job_store.py:620-629` 明确最后轮无完整终态时恢复 failed，结果为空但已提交轮数保留；`:634-651` 覆盖零／部分轮持久取消，结果为空、轮数保持、取消响应快照不变、后续非法轮次提交拒绝；`:963-980` 精确检查 running/progress/cancelling/cancelled 的版本递增。
- `test_job_store.py:184-187,305-355,376-415` 的原子故障矩阵包括 after_commit、异常／注入取消／真实进程退出；重开后完整状态／版本／所有权等关联核对，after_commit 分支明确保留 succeeded。`:343-344` 特别声明注入 KeyboardInterrupt 不等于持久取消请求，不能把这个矩阵夸称成所有真实取消竞态已经运行证明。
- `test_job_store.py:161-169` 的原子成功后取消断言目前只精确到 disposition；比逐轮用例的完整等值断言弱。若 owner 要补充同一时间语义在 read／atomic 上的独立可达反例，可扩展为完整 Job、结果、marker、版本前后相等，但“尚可加强此断言”不是现有错误输出的证据。

### 可交给 root/T01 的具体问题与最小计划

1. 请 owner 裁决 `states.json` 是“跨实现抽象上限”还是“当前 JobStore 必须实现的每条持久边”。原规则和当前同事务实现应给出一致说明／trace refinement；不能未经裁决删边或把成文规则改成 design-only。
2. 若抽象边仅表示迟到取消的观察竞态，记录当前实现用 `running→succeeded`＋`alreadyTerminal` 满足它；保留“取消先到不得部分成功”的强约束。纯谓词测试与实际 JobStore 次序测试应各标其证据层，不虚称相互替代。
3. 若 owner 确认必须存在真实持久 `cancelling→succeeded`，先提供可实现且不违反“终态不可改写／同事务发布”的状态设计及失败反例；不可为覆盖枚举边而人为插入 cancelling、伪造 True 或放宽通知来源。
4. 如进入新候选验证，优先测试两个合法次序、丢响应／重开，以及取消先到时 database dump／结果／marker 不增的精确反例。当前没有授权运行，未实施该计划。T05 不修改共有文件，结论仍待原意见处理／指定审查门禁裁决。

## §8.2：三份语料的固定锚与现有哈希门

### 可证的消费结构（static）

- `packages/engine/tests/test_contract_v2.py:16,24-36,204-219` 从 fixtures 读取 expected `valid` 等值；`test_binding_regressions.py:9-14` 同样消费语料；`test_frame_corpus.py:12,66-85` 比较 expectedFrames／expectedErrors／terminal。TS 对应消费者为 `tests/unit/contract-v2.test.ts:2,29-44`、`binding-regressions.test.ts:3-10`、`jsonl.test.ts:3-25`。
- 包内 `packages/engine/src/ontolearn_engine/contract_probe.py:10-28,30-51` 读取同三份 JSON 再比对本包适配器／reader。该入口是供包验证运行的共享例工具，不等同于业务引擎每次生产请求都会运行的独立审查者。
- 这些消费者没有把上述三文件先与某个独立硬编码 expected SHA-256 常量比对。因此，某一个依赖语料的比较式中，若同改函数行为与该条 expected，比较式可能仍为真。这是 static 条件推理，不是整套测试全部通过的证据。
- 原报告称 `test_frame_corpus.py:52-63` “只固定数量，不固定内容”，若限于该段字面确实是 counts；但整个文件还有 `:38-43` 对中文 UTF-8 内容的精确断言及 `:82-85` 的完整帧／错误／终态断言，不能扩大成整套没有内容断言。

### “仅 registry 被 hash 锚定”的准确边界

1. `packages/engine/src/ontolearn_engine/resources.py:21-22` 的 REGISTRY_HASH 是对当次 registry bytes 动态计算，而非某个预先批准的 literal digest。
2. **同一文件 `resources.py:49-55` 对 Python adapter 及全部 `v2/*.json` 逐文件计算 SHA-256**；三份语料都属于这个 glob。原报告如意指“根本未对它们做 hash”，则与现有代码不符。
3. `scripts/verify-i04-package.py:32-47` 要求包内 `frozen` 为真，并把包内资源哈希集合与源码全部相同文件的动态哈希做完整相等比较；`:48-57` 再执行包内公共例。它是包／源同源与携带完整性的门，能发现“包语料与源码不一致”，不能发现“已把错误 expected 与源码一起批准”。本轮未运行该门。
4. `apps/desktop/src/main/engine.ts:267-279,350-359` 对 registry bytes 做结构一致性及 hash 协商；`test_coordinator_control.py:28-32` 比较 hello 与同源 REGISTRY_HASH。registry 此门用于双端同版本，并不天然防止双方源码／registry 锁步同改；将三语料“按 resources.py 的 REGISTRY_HASH 同法”处理，若仍只动态计算同源 digest，就不会获得独立固定真值的防同改能力。
5. 三语料在本次固定 Git ref 下有上表精确 bytes／SHA；固定 Git 与冻结评审机制提供版本身份，不等于测试里已有独立 gold pin。三种证据必须分别称为：固定版本身份、包／源一致性、独立预期基准。不能用第一／第二种冒充第三种，也不能说第一／第二种完全不存在。

### 需求、现行缺口与可证范围

- 原 S2 要求共用版本 schema／错误码／成功失败样例及双端一致：`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md:109,113`；I03 `acceptance.md:8-12,17,30` 要求完整正反例、实际输入原件 SHA 和跨端一致。没有在所查这些条款中找到“每份可演进共享例必须具有独立硬编码 bytes＋SHA，并在任何正常修订时强制失败”的特定现行要求。
- 原稿给的 `docs/reviews/I03/inputs/sources.json:1-25` 先例 pin 的是外部总控原输入副本；`docs/reviews/I03/handoffs/I05-contract-source.json:1-12` pin 的是交接原件／未冻结设计输入。它们支持来源可追踪实践，但对象和授权门与可随契约版本修订的共享测试语料不同，不能单凭先例宣布存在同一项强制验收遗漏。
- 本轮可确认的潜在门缺口是：测试 expected 与实现的独立性没有由这些消费点的固定 digest 门强制维持。它可能是有价值的供方硬化项；是否已违反当前权威门，取决于 owner 能否指出原有不可共同修改的黄金基准和独立批准规则。
- 尚缺：一个固定当前规范要求被违反的合法／非法输入、当前错误的实际 accepted/rejected 输出、具体变异范围、保留的独立测试断言及整套结果。原稿的“同时改 valid 与实现，所以三套和 probe 全部仍通过”没有提供这些条件；本轮不能把它登记为复现。
- 现有独立内联断言不是零：如 `tests/unit/jsonl.test.ts:27-95` 对 UTF-8、逐帧限额、重复键、坏 JSON、32／33 层等直接定义输入与完整预期；`test_contract_v2.py:39-58` 和 TS `contract-v2.test.ts:152-169` 的完整状态矩阵也不从三语料读取 allowed 集。某些实现＋语料同改会被这些断言拦住。不能未经具体反例声称“一起改一条 valid 即保证全部绿”；同样不声称这些内联断言覆盖了每种未来语义漂移。

### 可交给 root/T01 的最小计划

1. 先把“没有独立 literal gold pin”与“已有全资源 SHA／包源一致性”并列记录，保留原报告与严重度供 M／owner 裁决；不改写为“完全未 hash”，不据此替原报告判通过。
2. 请 owner 确认是否确有批准过的不可变语料版本，以及批准者、允许变更范围、变更审核门、hash 存放位置。若采用独立 pin，应由明确不同于可随实现同改的批准来源控制；把 pin、语料、实现全部放在同一可随意修改的候选中，仅能增加可见 diff，不能单靠 hash 禁止锁步修改。
3. 若批准硬化，新候选可加入三语料 bytes＋固定 SHA manifest 和专门校验入口；任何预期修订须明确 diff／规范依据／批准记录，不能靠更新 hash 自动获得语义通过。反例至少应包括：只改语料字节被拒绝、包旧源新被现有同源门拒绝、实现错误但 expected 未改被语义断言拒绝，以及同时修改 pin 的行为按授权门处理。不得把动态 REGISTRY_HASH 照搬当作独立 pin。
4. 在 owner 未证实当前强制需求或具体产品反例前，不将 T05 `source-identities.json` 的特定 pin 自动平移到共有契约。T05 的 oracle 纪律可作为设计参考，不能代替共有供方需求和写权。当前没有授权修改／执行上述措施。

## 交付判定与未解决限制

| 项目 | 本轮确定事实                                                                                                                          | 未确定／供方待裁决                                                           | 保持状态                                     |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------- |
| §8.1 | 条件边存在，三消费者 False，JobStore 正常路径不产生该持久边；迟到取消有 alreadyTerminal 路径和直接测试断言；通知 False 有明确规范依据 | 抽象状态边如何映射当前原子实现；是否存在违反完成／取消时间语义的合法产品序列 | 原 [中]，reported-open-awaiting-adjudication |
| §8.2 | 消费者无独立 literal corpus pin；全部 v2 JSON 已有动态资源 SHA 和包／源一致性门，registry hash 亦为动态                               | 独立 golden corpus 的原强制要求／批准权、具体当前产品反例及变异整套通过证据  | 原 [中]，reported-open-awaiting-adjudication |

本轮只有 static 原件、引用和因果推演；已有测试代码不计本轮运行通过。不触碰共有 owner 文件，不消除原 M B150 NotPass，不改原15 open，不签父模块、产品、性能或发布验收。
