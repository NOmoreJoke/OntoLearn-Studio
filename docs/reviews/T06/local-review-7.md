# T06 3be0397 资源修复候选完整本地独立对抗审查

日期：2026-10-22。审查者：`/root/s1_indexed_complete_independent_review`。本报告是完整当前候选的本地独立审查，覆盖私有行为计划器与 T09 固定输入适配；不是只审新增 patch，不是指定 ZCode/MiniMax 外审替代。

## 结论

**当前固定候选的独立 S1 私有范围：通过。未发现新增 P1/P2/P3 实现缺陷。**历史 P2-1 所指可避免的全对扫描、逐写全事实序列化、逐动作全候选排序/比较已经修复，完整可观察语义经本轮独立检查保持。**历史 P2-2 仍作为 P2 容量风险保留，成本没有消失；本次判断其不阻断当前私有 S1 范围，但不关闭容量验收或认可生产规模。**这项裁决理由、实测值和未验边界见下文，不能简化成“两项资源问题均已解决”。

判定依据是当前接口必须完整交付 B×E 个独立 JSON 决定，本轮确实复核了 100 万条完整结果、各独立 conditions 容器及完整计划哈希。输出本身有 Ω(BE) 空间/时间下界；PRD Q5/10.2 未规定当前输入规模、设备或内存/时间阈值，不能以未批准的默认阈值判其违约，也不能删矩阵、分页、共用可变容器或新增拒绝换取通过。当前能力仅为显式调用的私有纯计划函数，无公共/Store/真实运行注册；没有观察到结果裁剪、身份串扰、异常漏出或本候选新增的该类成本回归。因此，本次就**现合同的私有实现**作通过判断；P2-2 的工程容量风险和 Q5 的缺失仍真实存在，不能据本报告据此自动授权正式集成/发布。指定双方须对新候选独立重新判断，原 613 的任一 Pass 均未沿用。

## 固定来源、隔离与读取范围

- 唯一工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-resource-independent-review-3be0397`，detached HEAD。
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；product/HEAD：`3be0397faf03de6520c47bf7d86f3dc2fd004287`；对照旧实现：`61396a598b2dffc1d3d2fd4660f9af1d5c93d266`。
- 当前 AGENTS 全文读取，SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，前后保护 dirty，未还原/暂存。未切分支、提交、推送、开 PR；未改源码、受审测试、依赖/锁、配置或公共文件。
- 全文读取 3 个行为源码、5 个测试、fixture 作者脚本、3 个接口/适配/probe 文档。`counterexamples.json` 全量解析、结构及全部预期字段由原测试核验，作者脚本在自有 out 重新生成，完整规范 JSON 相等；没有把 7863 行 JSON 的显示截断当作完整读取。作者脚本不导入计划器。
- 重读 PRD FR-600–604、附录 C、E.1/E.2、G.0/G.3 和 Q5/10.2。PRD SHA-256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`。
- 读取 local-review-1..6 全部原文、round-1 两份完整原外审、ZCode process addendum、两份 owner audit、resource-remediation-plan 与独立处置复核。它们均为旧候选共同历史，不当作本候选通过证据。未读取当前 UI 外审输入/会话/意见或其他开发线意见，未访问凭据或当前 UI。
- 完整 base→product `git diff --binary` 重算与收到的 patch **6075356 B、SHA-256 `569b98c2b6f16a18593fc3c3c8b17580f8df21672d04188549d7946cda9c916f` 全字节相同**。76 个 diff 块的文件模式、blob/header、hunk 数、字节数和 SHA 均登记于 `out/independent-resource-review/source-and-diff-audit.json`；其中 4 个 archive binary 块仅作为历史流程证据核元数据，不执行归档历史脚本。13 项实际产品来源相对 base 全为新增，合计 11839 行；不能将其余流程/UI 历史材料误当新产品执行器。
- 运行使用本树独立 node_modules/.venv/out。没有 GUI、native、Electron 运行、HMR、CUA、模型 API 或网络外联；`npm run check` 只包含静态/单元/构建验证，不是桌面原生验收。

13 项实际文件逐一与 product Git blob 逐字节相等，且与派发 manifest SHA 相同：

| 来源 | SHA-256 |
| --- | --- |
| `docs/iterations/T06/interface.md` | `47fcdd948f838779f8c921ae7fcc48b586c8d24325e68f5a775b6b8670e4e2a0` |
| `docs/iterations/T06/probe_t09_baselines.py` | `d960d1c95e34d40398bb9a280745bdf690020e47b6730d8f59d45e6efba16565` |
| `docs/iterations/T06/t09-adaptation.md` | `0a48144fa3324c406af52848676c2f2e14840bf79747891d07f7a1709c7eb477` |
| `packages/engine/src/ontolearn_engine/behavior/__init__.py` | `0519496083ecaf23ad3a606c8be5f461b21bfb1507f313678083d212cec676d9` |
| `packages/engine/src/ontolearn_engine/behavior/baseline_adapter.py` | `18f6eb0133b12db950d07dfffe881fb38192af4b14d0b67003c47b67af5a32af` |
| `packages/engine/src/ontolearn_engine/behavior/planner.py` | `525caeb1aafadc9856dc912e50fec95dfbcaea568e64b911f783d0d7f42a95d0` |
| `packages/engine/tests/test_behavior_baseline_adapter.py` | `59a07e8b8d7f0caba8cca1d4f31f684fefafc295473f10ee0dd165439ed50859` |
| `packages/engine/tests/test_behavior_creation.py` | `96e99469d2057e56fd702d43bc3c0373e90809e6f624e49a5a19f675222d999c` |
| `packages/engine/tests/test_behavior_failures.py` | `02f9698299f224019e9aed01617d108a06cd4a16a591c5ec08624b2c9c96839e` |
| `packages/engine/tests/test_behavior_planner.py` | `940e54c1a94ec1b0ac9a8baec0bf7d98270fcaff2a476818033571a78db3285d` |
| `tests/fixtures/behavior/build_corpus.py` | `9bbe4db97895c5ead7588acf22a25fa21e5358743b83755a9549141f5b66c5b4` |
| `tests/fixtures/behavior/counterexamples.json` | `17de133b6a13efd14197b4d7dc09a51c7df097db5161b9acb6f7b92e5f9796f9` |
| `packages/engine/tests/test_behavior_resource_equivalence.py` | `9bb385e714156ee41b1cbf113063dda52c7fe007e240c58df08459d66d861e8f` |

## 当前实现语义复核

| 约束 | 当前证据与判定 |
| --- | --- |
| 先验证再索引 | planner.py:136–164 先拒绝重复对象/事实/单值矛盾，再于 175–183 建立索引。独立重复对象/事实、false 与 0 单值并存、通知/对象身份冲突负例保持原错误与完整 evidence；未被 set/dict 静默修好。 |
| typed JSON、槽索引、增量 effect | 192–207 先验证事实与基数，再用 `_json(fact)`，单值仅访问本槽；同值返回 unchanged，false/0、1/1.0 仍不同；272–277 输出规范排序。无对候选逐动作全量比较。 |
| 事件、删除与声明 | 210–270 的 create/declare/delete/remove 与事件阶段共用索引；删除自身与所有 relation 入边，重新 declare/create 不恢复旧事实。adapter 的 `_edit` wrapper（280–288）保留且只接经 model_state 校验的状态。 |
| 冻结和推导绑定 | 751–791 校验 current/binding/assertion_digest/ontology/rules；只读 frozen=事件后断言并推导并集，事实键集一次生成；条件只查 frozen，不见后续动作。人工重新贴标旧事实仍不证明推理真实执行。 |
| 首个竞争对 | 688–726 按槽保留最早 `(instance, typed value)` 代表，只用于查找，完整 intents 不裁剪。首 unique 无冲突时，两种剩余组必跨组冲突，第二 unique 可定位首 left；跨桶按原 `(i,j)` 取最小。没有“最早闭合桶”替代原首对。 |
| 动作与实例 | 858–875 保留四层顺序与 1000 源动作边界；create 全 initial 是一个源动作。879–905 每实例 scratch 从相同 after_events 重建，不见 peer create；同实例中间写及 create 初始中间单值仍参与跨实例竞争；同值不丢通知和其他动作。 |
| 失败与消费 | 882–953 保留完整/前缀 decisions/intents、准确 action/initial 位置、discarded 前缀，executed_actions=[]、committed=false，无部分 candidate/consumption。956–983 成功才返回消费候选；事件 fingerprint 排除 sequence、scope 必须一致；未保存或提交账本。 |
| 固定输入与投影 | adapter 保持 manifest/PRD/所有文件 hash、越根拒绝、同一 verified buffer 解析，不导入 T09 Python/不读取 expected 充当实际事实；project_candidate:490–583 复验 subject/predicate、通知/事件/生成类型 IRI，保源动作和完整结果。 |
| 输出完整性和隔离 | 807–855 保留全部行为×accepted event 决定及每条独立 conditions；954–983 保持 before/after_events/frozen/candidate、完整 Diff、通知执行顺序和消费。私有结果跨调用与关键状态分支修改不串扰；无全局可变 workspace。 |

## 实际独立验证与原始证据

以下全部针对本树固定 3be0397 运行。每项 stdout、stderr、完整 argv/cwd、真实进程 exit 均保存在 `out/independent-resource-review/` 对应 receipt，不用展示用 tail 或 shell 管道状态替代 child exit。

| 验证 | 实际命令/证据 | 实际结果 |
| --- | --- | --- |
| 全仓检查 | `npm run check`；`check.receipt.json`、`check.stdout`、`check.stderr` | exit 0；15 TS 文件/630 测试、1191 Python；lint/格式/类型/构建/ruff 通过。Python 57.67 秒是本次 pytest 汇总，不是产品计划性能。 |
| 全部行为专项 | `PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -p no:cacheprovider packages/engine/tests/test_behavior_baseline_adapter.py packages/engine/tests/test_behavior_creation.py packages/engine/tests/test_behavior_failures.py packages/engine/tests/test_behavior_planner.py packages/engine/tests/test_behavior_resource_equivalence.py -q`；`behavior.receipt.json` | exit 0，139 passed。没有修改测试预期。 |
| 自编独立对抗脚本 | `uv run --frozen python out/independent-resource-review/adversarial.py` | exit 0；87381 条二实例/二值、长度 0..8 序列穷举，按直接 combinations 定义比较首写；另 6000 多槽/typed/create.initial 输入，完整首对与独立 oracle 相等。 |
| 全管线差分 | 同脚本，固定随机种子 2026102207；旧实现仅从固定 Git 导出到自有 out 后导入，SHA `9d2474a377c3d57da28aed0461e33d1846f21e34c8a862749122e029b522970a` | 1520 例：730 plan/790 domain error，全部规范化完整 plan 或 reason/location/evidence 相等，无 unexpected exception；滚动 SHA `4923550a13d75251dd9bc8c3006f8ab1533a462bb90083f12d831b41c1af7fd5`。 |
| 负例/所有权/续轮 | 同脚本，显式重复对象/事实/单值、通知碰撞两个方向、dynamic initial[1]、非法删除身份、事件删除重建/入边/typed remove、跨调用修改及重投 sequence/异内容 | 全过；输入完整不变，失败无部分候选/消费；准确 initial_index=1，换 sequence 重投 no-op、换版本异内容拒绝。每例全证据差分而非仅数目。 |
| 非重复槽补充 | `uv run --frozen python out/independent-resource-review/extra_cases.py` | exit 0；20 create×10 个不同单值属性并附通知，全部旧/新结果相等，200 facts/40 源动作。此项不是沿用“每 create 重复同槽50次”的资源输入，也不据此外推容量。 |
| fixture 来源闭合 | 自编脚本在 out 用当前作者源重建，未复制到或写入源 fixture | 整个 corpus 规范 JSON 相等，包括全部请求与 expected。 |
| 批准 T09 固定字节 | 只读原批准缓存，逐件与 Git `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 比字节后复制到自有 out；`t09-byte-audit.json` | 19 件全部相等：17 manifest 文件、manifest 与 PRD；manifest SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`。没有读取变化中 T09 代码。 |
| 九例 T09 完整 probe | `uv run --frozen python docs/iterations/T06/probe_t09_baselines.py --source-root out/independent-resource-review/t09-approved-873c8c0 --manifest-sha aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e --output out/independent-resource-review/t09-probe.json` | exit 0；九例全部完整事实/工单/通知/动作顺序/消费/冲突比较成功，输出与 owner 当前原件全字节相等；MANUAL GOLD、not-executed、formal_acceptance=false 保留。 |

本轮没有产品验证失败。**本轮自有测量比较外壳曾真实 exit 1**：create800 的测量 child 已 exit 0并留下完整原件，外壳错误把 owner 的命令 receipt 当成含 `result` 的测量对象，随后 `KeyError: 'result'`，matrix 尚未启动。修正为读 aggregate manifest/实际 stdout，直接比对已保存的 create，不重复运行；matrix 另行执行并 exit 0。原 child stdout/stderr/receipt 与 `measurement-wrapper-first-failure.json` 保留，不把首败记成首次全部成功。

本轮另有一次**读取历史证据的辅助脚本**使用系统 `python3`，其版本不支持 `zip(strict=True)`，真实抛 `TypeError`；同一 shell 后续只读命令继续后整体 exit 0，不能把这个外壳状态称为该辅助 Python 成功。随后明确使用项目 `uv run --frozen python`，完整10原行逐件字节/SHA校验成功。失败没有执行产品代码，记录在 `owner-first-failures-audit.json`，原工具输出保留。

已全文读回 owner 原始首败精选10行（5 call/5 output，40492B/SHA `8187b04d159b6e22fe2d2071cbb3216c9b95ad3857f722772f0f84066d4161db`），路径 `/Users/kyle/Documents/工作/知爻/本体/outputs/20261022_t06_resource_fix/owner-first-failures/`。与manifest逐行字节/SHA一致，源原行号及offset可追踪，不是重演：5853/5857 ruff check过但format exit1；5861/5865格式化后收集exit2，adapter仍导入被删 `_edit`；5876/5880恢复兼容wrapper后122 pass/exit0；5892/5896新增测试E501，随后17项为1 fail/16 pass，失败是JSON字典键插入序的raw dumps比较；5900/5904改为sort_keys而保留typed值/事实列表顺序/trace/diff后139 pass/exit0。本轮静态核对当前wrapper和精确断言，并独立139全过，所述历史失败已修，原首败不被最后成功掩盖。

另独立读回 owner 的 13 份本候选 receipt 指向的 **26 份完整 captured stdout/stderr**，字节数/SHA 全符合，13 真 exit 0；核验登记在 `owner-raw-streams-audit.json`。owner 的 1009 差分（114 plan/895 domain error）是其证据，不冒充本轮新设计 1520 例；本轮有独立输入与 oracle。未用旧指定报告中的 tail 汇总代替当前完整日志。

## 两项资源 P2 的本轮处置

### P2-1：原报告可避免的二次扫描——已修复本次指向的机制

当前对应位置是 planner.py:175–207、688–726、781–789、950–955。事实写只查 typed key 和受影响槽；冲突搜索不配对无关槽；candidate effect 增量计算；候选/事件后状态仅在边界排序。per-instance scratch 仍重建，成本并非零，也没有证明任意事实/字节规模都可接受，但原指向的逐写/逐动作全量扫描与全局无关 pair 已不存在。

owner 的精确配对测量（先旧后新、fresh process、同输入/完整计划 SHA 相等）保留原值：

| 输入 | 旧 613 wall 秒 | 新 3be0397 wall 秒 |
| --- | --- | --- |
| 200 create，每个同一 status=S1 重复 initial50 次 | 8.675141 | 0.169952 |
| 400，同上 | 33.184808 | 0.322635 |
| 800，同上 | 131.515803 | 0.636688 |

本轮读取经过核验的当前 helper（SHA `25dfed41f78bf9d9954f5bbac5c19e83ffda50a8b961965fd9556a3ca3bb7df9`）复制到自有 out，以同一精确800输入独立运行当前实现：**wall 0.640106 秒、800 决定/800 源动作**，tracemalloc 关闭。input SHA `400f6c0092085c16fc1060095707e78ee81926be30c43221ca1e85e7723c2da1`，完整 plan SHA `54644b5221148575a4f43395cd479e470e1b0e4a3176b683d22e9736d3cba33c`，均与旧/新配对原件相同。命令完整 argv 见 `creates-800.receipt.json`；仅加载固定旧文件供身份核验，未重新执行旧131秒规模。

这只证明该环境、该精确合成输入下的机制修复及实测；不是 50 个不同属性，不是生产响应时间或速度倍数承诺。1000 源动作本来就不是 facts/fields/bytes 容量配额，不能称“旧限额被 initial 绕过”。原 P2 严重度不改写，关闭的是本次已定位并修复的可避免机制，容量总门未因此关闭。

### P2-2：完整 B×E 决定输出——风险保留、当前私有 S1 非阻断

位置：planner.py:807–855、862–875、979；interface.md:28。合法反例仍是1000不匹配行为×1000事件，**零动作、100万条完整决定**。源动作上限不限制这些记录，内存和时间会随组合数增长，未触发组合不能称绕过动作上限。

owner 同口径旧/新原值为 Python traced peak **345860759 / 340522343 B**，开启 tracemalloc 时 wall **11.622307 / 11.710348 秒**。本轮独立运行当前精确输入得到 **340522343 B、11.484832 秒**；这不是 RSS、不是关闭跟踪后的耗时。测量区间是 prepare_events＋reasoning_input＋plan_behaviors，不含测后完整输出 hash/核对。input SHA `1a0a2c59b5286440a19b3bcb4c5e990f20a1758df125f4a7eb378d006837a782`、完整 plan SHA `0964fe0afbe22f4d337b2fd5aaaa72d5f38f37c99aee7bf7b88f95f49b509f10` 全相同；逐 row 完整字段、顺序和100万个独立 conditions 容器均核过。命令见 `matrix-1000.receipt.json`。

**成本没有被优化掉，不把约340MB说成资源问题已关闭，也不改变 P2 严重度。**本次不据这项风险阻断纯私有 S1，理由在结论中已明确：现合同必须材料化完整输出，没有批准容量线，未证明当前私有语义或既定预算违约，且必要成本仍如实交付/披露。这里已作当前范围的实质裁决，不以“装配前再说”代替本轮判断。与此同时，对“正式设备/规模可用”“取消可响应”“内存/RSS预算合格”“同事务序列化/持久化可靠”的主张，现证据仍不足，不能判通过。若将来要改变输出合同/新增配额，须由对应 owner/PRD 决定；本报告未替 Q5 填默认答案。

## 全部历史意见逐项处置

| 来源/级别 | 本轮状态 | 当前复核依据 |
| --- | --- | --- |
| LR1 P1 静态 create 破坏重复/空轮 | 关闭，未回归 | `_static_references` 仅登记常量供后续本实例引用；触发才编辑；重复/空/disabled/mismatch与新事件真实碰撞回归、独立常量续轮探针通过。 |
| LR1 P2 冲突/Diff 缺完整断言 | 关闭，未回归 | 九例 fixture 的全 decisions/intents/conflict/event_trace 与完整非空 diff 等比较；本轮139专项与自编整结果差分均过。 |
| LR3 P2 事件校验缺阶段/源位置 | 关闭，未回归 | 预校验/冲突/编辑失败精确 source event_index 与合法 ID/sequence 保留；反序请求和排序后冲突测试实跑通过。 |
| LR5 P2 展开身份非法 IRI | 关闭，未回归 | adapter 投影全事实subject/predicate及通知相关IRI复验；四非法展开subject与事件IRI负例实跑通过，失败不改 plan。 |
| LR5 P2 dynamic initial 无索引 | 关闭，未回归 | `_resolved_action`逐字段解释；旧精确回归与本轮独立第二字段缺失均带initial_index=1，无候选。 |
| LR2/LR4/LR6 原 Pass | 不沿用 | 本轮重新读当前完整实现、运行139专项与独立探针；旧结论仍只属于各原候选。 |
| ZCode P3 sequence 未点名 | 已澄清 | interface.md:7 已明确排除sequence；代码内容身份与续轮sequence变化no-op相符。 |
| ZCode P3 动作JSON标量边界 | 已澄清 | t09-adaptation.md:12 明确动作值原样JSON标量，不冒充完整RDF literal codec；没有新增一般RDF支持。 |
| ZCode 信息 rdf:type集合 | 维持原边界 | adapter model_state仍为many，不把singleValuedPredicates误用于类类型集合。 |
| MiniMax P2-1 | 当前定位机制已修 | 详见资源节；保留原P2事实、精确输入纠正与未验容量，未改原报告。 |
| MiniMax P2-2 | 保留P2风险，当前私有S1非阻断；容量未验 | 详见资源节的当前独立裁决与实测，不能登记成成本消失或指定外审已关闭。 |
| MiniMax P3-1 initial顺序覆盖 | 已澄清、无新拒绝 | interface.md:26明确有序后写覆盖及中间单值仍竞争；全initial保留在单个源动作；没有按建议暗加cardinality错误。 |
| MiniMax P3-2 同对象create碰撞 | 已澄清、现合同符合 | 同行明确对象分配碰撞拒绝，不等于属性同值幂等；declare仅事件允许。create/notify两个方向碰撞精确失败。 |
| MiniMax P3-3 成功源位置 | 未扩展，非现合同缺陷 | 当前只承诺错误源位置，成功仍ID/理由，PreparedRound保原请求；消费schema/指纹不擅增位置字段，未新增成功定位承诺。 |
| MiniMax P3-4 Diff含事件 | 已澄清 | interface.md:34明确before→candidate总净变化；不把frozen只读推导缺席误记行为删除，不新增未批准Diff。 |

旧指定过程门单独保留：ZCode真实是4次PreToolUse拒绝、均未执行；后继stdin首跑20 PASS/2 FAIL/exit1、修正5 PASS，合计27条结果，“两次/26条/全过”原概括失准。补正不改原报告，补正轮另有prettier新命令，不能泛称未重跑任何命令。MiniMax原check/122专项含tail、实际argv与上游完整stdout缺口不倒推；probe15/16/18/22/23/24及取消13首败/修正链以owner原件说明保留；probe17同槽重复与tracemalloc/RSS口径已纠正。本轮未重试或执行任何归档被拒脚本，也不以当前独立验证追认旧过程合规；该门仍归总控/指定流程裁定。

## 未验边界与最终状态

真实推理/通用 RDF codec；真实 Store 原子轮次提交、回滚、取消、迟到响应与恢复；资源队列/产能 B-07、轮末推理/指标及完整 E.2/G.3；Agent工具失败 B-08；公共方法/受限错误/权限/轨迹交接、UI正式接线；设备规模/并发/RSS/端到端持久化容量与 Q5；GUI/native 两OS、Electron/e2e/HMR、包内运行/真人操作、远端CI/push/PR/正常合并/生产均未由本轮验证。九例只给人工 gold 纯计划比较，不能升级为正式G.3或父FR-600–604完成。此处静态确认未注册公共执行入口，不等于公共链路已验收。

**实际终态：本轮完整独立 S1 审查完成并通过上述私有范围；P2-1定位机制关闭，P2-2风险/容量门保持，指定新双审及所有未验门保持。**唯一文档产物是本报告；脚本/日志/缓存仅写自有 out，源13件、HEAD和保护AGENTS前后保持。没有改原开发树、旧报告或公共状态，没有向指定reviewer发送意见。
