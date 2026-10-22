# I05 固定 deadline 的有限静态归因

结论：本轮失败真实触及固定120秒合作式边界；现有证据没有显示可通过删除 collector 重复工作直接解决的主要瓶颈，也不能把 wrapped API 的墙钟时间等同 canonical CPU、产品性能缺陷或并行负载因果。建议先保持实现与120秒/64MiB条件，协调一次有明确资源隔离前提的原 full-v1 控制验证；本审查不执行它、不授予通过。若仍不足，再为 owned probe 的真实调用计数 instrumentation 提出单独有界方案，不能通过放宽预算或减少观察求绿。

## 已核固定输入

只读主树 `.worktrees/I05-pytest8-supplier-integration` 的现行 AGENTS、父任务指定源码相关函数、两份既有 JSONL。完整pytest终态由父任务回告，本审不重新执行或代审全部JUnit。未运行产品、pytest、formatter/linter、benchmark、CLI、GUI或OS profiling；未读别线WIP或修改产品/历史报告。计算程序仅用固定Python3.12标准库解析字节、JSON及AST。

- probe：102749B / `2996deca33083754132bf5f4eab8d1e273161b3e5fe722a8ee96856fb5cc0d5b`。
- test：76535B / `5fcf853fb48f5781758bdb0893357a9687f1ce7e35d9cc9352957b7d4fcaa4c9`，对应本次分析开始时点。父任务后继修复不由此身份预先覆盖。
- shared：`build/i05-pytest8/full-pytest-02/semantic-full-v1-diagnostic0/observations.jsonl`，46483457B / `a84bfcaa1b374fc02a8114aedfc414b2f6a36368c6b2176bd4a7397f15350a1b`。
- producer-fault：`build/i05-pytest8/full-pytest-02/test_r1_real_producer_capture_0/observations.jsonl`，17290993B / `23f6dd18a937edb3761ba3ebcca0eb65f1c9d92e630947ecc4b68880e9f2e71c`。

shared为220条记录：header、218条observation、terminal；terminal有199个unstarted IDs，collectionComplete=false，elapsed121.103670秒。首失败为 `fullview/profile-76`、`semantic_profile_restore.restore_profile_result`、`restore/result`、`COLLECTION_DEADLINE`。最后一次restore的attempt记录returned=true、约1.665310秒；源码在调用后再检查全局期限，故“实际调用已返回但总预算越界”与该流相符，不代表该观察已成功通过或整个结果完整。

fault流为188条记录、186条observation，elapsed83.279452秒，在 `dag/type` 的 explanation restore 出现测试故意注入的INTERNAL_ERROR。它是生产者故障保存回归，不是第二个完整full-v1成功样本，也不能用它推算余下199项总耗时。

## 时间归因的已知与未知

| 既有shared流范围 | 实际墙钟区间 |
| --- | ---: |
| terminal elapsed | 121.103670秒 |
| 218项observation的start/end区间之和 | 119.258929秒 |
| 上述观察区间内，checked-call区间的并集之和 | 117.698376秒 |
| 观察区间内但不在checked-call区间内 | 约1.560553秒 |
| terminal elapsed减全部观察区间 | 约1.844741秒 |

使用每项内的区间并集，避免嵌套attempt双计。后两项是边界差值，不是单独序列化计时：它们还包含准备、计数器进出、字段编码、检查、header/writer等；不据其给任何一项CPU成本。checked-call自身又包含真实业务、`sys.setprofile`回调、audit hook、解释器调度和同期负载，不能把这些墙钟数字拆成未经测量的纯业务或计数器开销。

最主要的实际checked API累计为：82次 `semantic_execution.execute_profile_records` 73.973387秒；36次 `semantic.query` 14.211652秒；19次result restore 13.000742秒；14次admitted production 7.282285秒；27次explanation restore 4.888540秒。它们是包含失败attempt的instrumented累计，不是独立S1基准或峰值/容量验收。

collector确有每次 `_catalog` 重读并strict-parse固定schema的工作；production每项也独立prepare、compute、capture expectation及restore。源码没有跨case成功缓存。当前区间证据没有把这些原调用之外工作定位为主要耗时；以schema缓存、共享可变材料或复用上次生产结果求绿既缺乏主要收益证据，也可能损害独立重验。此时不建议实施它们。

CallCounter对每项full-v1使用全局profile hook，读取每次Python call的code identity，仅计真实reason/validator；finally恢复原hook。该设计使instrumentation成本混在API区间内，但现有两流没有“同一调用无计数器”对照，不能断言它造成deadline。若后续隔离仍失败，更窄事件范围的真实计数设计属于可审的owned probe方向；必须先证明真实代码身份、嵌套/异常计数、既有hook拒绝和生命周期恢复，不能替换业务callable或对已知零计数案例直接停用观察。当前不指定未经核实的运行时API，也不承诺收益。

## 两流可比前缀与上下文

两流前185项具有相同ID和status，projectionSha256与callCounts全同；前缀result仅两个B1计时结果的canonical字节不同，其余相同。这只是这两次既有流的字段事实，不是外部oracle或source/package parity。

其中83项profile的观测区间shared合74.872438秒、fault合70.001318秒；共同前缀时段不同、后者处于同一pytest进程更后的运行和缓存状态，也没有独立负载记录，因此不能把差异归于单一因素。父任务传达T01 StageB从18:58 UTC起同期执行Python，仅可记“存在重叠”这一上下文，不证明竞争导致本次失败。本审没有读取别线进程/WIP或扩展OS研究。

实际JSON路径 `header.contexts.mathInputContexts[*].eligibleStandaloneMathInput` 是83项中82true/1false；83项profile观察的sourceCaseId全部能匹配对应context，实际78 observed-return、4 observed-rejection、1 not-executed，82次checked execute与代码一致。旧摘要中的“6/77”不是这份实际math域的可用事实，不能据此删77项或修改collector。其他context域未在本审扩查。

## 输出量边界

shared完整原始输出46483457B，尚低于67108864B cap；没有OUTPUT_REPORT_LIMIT或item cap触发证据。218项中profile-83行共15944142B、dag/fullview行14801473B、restore-negative行14892456B。最大单行为 `restore/explanation/tail-source-tamper` 1673258B，其中result约1671255B、receipts字段1176602B；相同生产数据在多个独立负例中重复记录是当前实际协议形态。

这说明报告体积与receipt表示值得在完整候选设计中保留关注，但不能由已经输出的218项断言未开始199项一定触cap，也不能删除receipt/观测、改为不同语义摘要或压缩换协议来掩盖完整性要求。writer已先编码并在暴露该行首字节前计总量、保留terminal reserve；应维持原始流和这些固定拒绝条件。

## 最小必要后继方案

1. 本轮失败矩阵、两实际JSONL和预算均冻结；header历史身份断言的最小修复单独处理，不混作deadline优化。
2. 由总控内部协调一个CPU密集验证窗口，确认已知同期T01 Python检查自然结束、没有另一条已知重型验证同时启动；不扫描或终止用户进程，不对系统施加新OS调优。记录该协调事实，而不是假称整台机器无负载。
3. 固定当前完整候选与原资产/锁/120秒/64MiB，使用原完整full-v1 pytest fixture的一次实际调用，保持计数器/observer及全部417声明不变，fresh自有pytest进程/独占basetemp，保存分流、JSONL、JUnit与前后hash。不重复已绿JS链，不先改deadline，不循环重试等偶然成功。执行前仍需主方授权并核资源前提，本审只给方案。
4. 若该一次仍越界，以完整新流确定下一个边界；再单独提出owned CallCounter以Python3.12 sys.monitoring窄事件计数替代全局sys.setprofile回调的纯源码方案，先核API契约、真实code identity/异常计数、监控资源占用与拒绝/恢复/清理以及现有hook测试，再独立审查；本次不实施、不实验、不预签等价或收益。若没有可证正确的替代，则如实上报固定条件与必要工作仍未满足。没有证据前不改预算、不缓存业务成功、不丢计数/观测。若一次完成，也只证明该受控运行完成，不证明并行负载因果、稳定性能、跨平台、wholeH或生产验收。

当前没有可由本审直接批准实施的已证语义修复，也没有任何性能提升量化。完整工程、指定双审及发布门禁由父任务继续处理。

父任务提出的上述两阶段方案在本证据下可审：第一阶段只修已证历史身份断言并控制已知并行执行混杂，collector/资产/预算不变；只调用原一个full_run节点一次，不跑已绿JS或其他1176项、不新CLI/native/OS profile。此为有预先规定条件和一次性停止规则的隔离核验，不是无条件重复求偶然通过。现有静态流已能排除若干错误优化方向，但不能证明未开始199项的完成、cap情况或实际纯计数器成本；没有更小的既有静态证据能替代这一次完整collector调用。第二阶段的选择性计数器方向仅是待核API与生命周期的方案，不是现在授权更改或测试。

## 对父方具体计划的独立评估

已全文读取 `outputs/20261023_i05_deadline_resolution_plan/plan.md`，当前3418B / `cc6a3319a49fa35b95cd99c40c899ca6c5aa184ffdbf6b652f0ac9b766c82e67`，原字节复制为本目录 `reviewed-parent-plan.md.raw`。结论：该最小两阶段计划边界正确、可审；未见需阻断该一次受控验证的已证问题。它不是现在已执行或已通过的证据。

实际核读当前测试953–981行：计划指定节点正是原 `test_full_jsonl_is_complete_inventory_not_self_signed_equivalence`，依赖模块级 `full_run`；fixture直接调用 `probe.run_fixed_suite("full-v1")` 一次，以BytesIO接全流，正常返回后无论status是否0都落原诊断JSONL。节点检查status0、64MiB、完整有序inventory、terminal及全套417项完成；没有以selector缩减内部观察。另核real_resources/canonical原fixture确实固定资源身份并导入真实模块，不是stub。它仍是既有pytest内受控验证，不能扩称干净独立CLI/frozen运行、observer先于canonical import的CLI证明或新native验收。

计划明确管理范围串行窗不等于整host idle，120秒为合作边界而非OS硬期限，失败自然完成并保首边界后不追加重试；不删417、不延120、不增64MiB、不重复已绿JS或另起selector/CLI/native/OS实验。这些条件保留完整性和本轮归因目的。一次通过不能量化改善、证明竞争因果或稳定容量；fresh pytest进程也改变此前pytest历史及缓存，因此更不能将差异单独归因T01负载。

后继选择性监控段写“本方案尚不实施该实验”，与root已有owned源码修复权限并不冲突：权限存在不等于当前方案已经批准具体改法；先另提API/占用/异常恢复/真实计数与代码身份的最窄方案、独审后再按主方决定执行，边界正确。本审不替该后续源码方案签等价，也没有为提出建议运行实验。

一处非阻断计数措辞可更精确：计划“其余1176项”意在避免重跑已通过1176项；1180总项中选择1项后的其余节点实际为1179（含另外3项本轮失败）。建议主方表述为“不重跑已通过1176项及其他节点”，避免把1176误作减一后的总数；这不改变当前明确给出的唯一nodeid或执行范围。本审未修改父计划。
