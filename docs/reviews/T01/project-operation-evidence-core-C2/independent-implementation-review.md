# C2 原操作证据核心独立实现审查

最终固定模块39943B/d6554289与测试50985B/9097ccb7的代码独审未发现未解阻断，支持作为本内部 C2 证据读取阶段候选交验。原五项 P2、取消清理通知与预算表列前界均已实际闭环，历史反例和观察身份保留于下文。新候选正常全仓检查与独立source实际终态已读原日志绑定（1125TS/3098Py/44原skip、12原源）；旧1c5d候选检查不覆盖本版。本意见不等于指定双外审、正式resolution/权限或父FR验收。

## 授权、输入与操作边界

- 树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-operation-evidence-core`，继承 adoption `f927f4188fc2d285b405f55ff7ca03f675340af2`。
- 已全文读本树 AGENTS，15852B/SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。
- 已全文读控制 `T01-operation-evidence-C2-implementation-authorization.md`，8820B/SHA256 `e17052d0e29534d95617023a69f63c1a3f2e5f2bbb04e03eaabe002f589f2b7d`；固定旧树实施方案42685B/SHA256 `e7db89cb52cc75707d0e7a00e637e97701bea7e7d49f623ef464cb1baf44b96b`。
- 审查者唯一写入本新报告；没有修改模块、测试、继承52件、控制规则，没有 stage、全仓测试、GUI、网络、模型或打包。
- 独立机制脚本只写 `/tmp`，使用本树 `.venv/bin/python`，实际新建自有临时 SQLite；损坏反例仅在该临时库 fixture 移除并重建原 immutable triggers，不修改受审产品或测试。

## 实际观察版本

| 材料                                  | bytes | SHA256                                                             | 用途                                           |
| ------------------------------------- | ----: | ------------------------------------------------------------------ | ---------------------------------------------- |
| operation_evidence.py                 | 36821 | `3bf20be44d5945c1b407a296543d0d607fca538b9ec5b97215613d0618c1883b` | 首次全文核读；P2-01/02真实探针输入             |
| operation_evidence.py                 | 36998 | `d8c927ee294c8400f3149e36a6caaa1614caa779de43aee92f3380f5c5ef1b91` | 主线开始修订后的实际输入；P2-03/04真实探针输入 |
| test_project_operation_evidence.py    | 32340 | `f85e5414f358c34950599b38584a9d6b29a4e0adeb2efc4f26b99cefcfc23489` | 初次读回；作者其后仍追加，非最终冻结测试       |
| project-operation-evidence-core-C2.md |  5310 | `7b78c8c8376d238c51d21e65b1e066f11375ed86c1adbce22245be98b00db4f5` | 初次实施边界说明                               |

来讯35965B/407fb版本不是实际上述探针输入，未据该过时身份声称验证。所有下列命令的完整 exec_command 返回对象均在独审工具流保留；exit0表示探针完整执行，反例的接受/拒绝由其实际 JSON 表明。

## 实证问题与最小修复建议

### P2-01：新读事务未核实际库头

位置：`read_operation_evidence` 的 `BEGIN` 后至原 `_preflight`。原 `_preflight` 不包含 `ProjectHostReader._read` 中的 actual header 检查，只核 owner._target_format 与 catalog 无法代替当前 `PRAGMA user_version`。

真实 JobStore3 原 writer 建立 queued Job，分别改临时库头3/0/2/4；读取全部返回 job-record，trace均未查询 user_version。每次 dump不变、事务释放，trace从BEGIN到ROLLBACK。

- 命令：`.venv/bin/python /tmp/t01-c2-independent-header-probe.py`。
- 完整工具结果：chunk `3a2fa3`，exit0，原源码3bf20be。
- 实际四条：actual3/0/2/4均 finding=job-record，headerQueried=false，unchanged=true，transaction=false。
- 建议：新事务内、preflight前经计数窄只读PRAGMA核 exact integer3，其余state；原继承52件不改。
- 主线已接受，最终版定点复核待补。

### P2-02：合法数值结果被当作缺证

位置：`_terminal` 对已通过同版 row contract 的 payload 调用 `_measure`，该计量器只接受 exact int、不接受合法 finite float。

真实 create→start_job→finish_read_job，单行cells为 `[1.5,1.0,-0.5]`；原 writer/contract 接受，Job实际 succeeded，但 C2 finding=incomplete-evidence。不能以此把已完成的正常读结果降成证据损坏。

- 命令：`.venv/bin/python /tmp/t01-c2-independent-result-float-probe.py`。
- 完整工具结果：chunk `7e8fec`，exit0，原源码3bf20be。
- 实际：jobState=succeeded，payload含上述三有限小数，finding=incomplete-evidence，unchanged=true，transaction=false。
- 建议：selector仍保严格安全整数政策；为已通过row contract的结果正文独立支持原canonical有限safe-range float计量，先有限/range判定，再做常数界标量编码；不能全面放宽selector。
- 已报告，最终修订与反例待补。

### P2-03：普通 Job 未核到当前 head 的完整必要历史

位置：`_job` 至 `_terminal`。仅atomic且marker存在时调用原receipt_for；ordinary/read/queued Job不读目标app_checkpoints/当前链，与授权及方案§6的完整目标history/当前state闭包不符。

真实queued test.read后再由原writer提交domain operation；fixture损坏该当前checkpoint.payload为`{}`并恢复原triggers。C2仍job-record，trace无app_checkpoints读取；同一实际库调用原format3._history明确拒绝。

- 命令：`.venv/bin/python /tmp/t01-c2-independent-later-history-probe.py`。
- 完整工具结果：chunk `c745a2`，exit0，输入源码d8c927ee。
- 实际：finding=job-record，historyValidator=REJECT，readAppCheckpoint=false，unchanged=true，transaction=false。
- 建议：确定目标internal后，通过view复用原format3._history核目标完整链；不全库validate，不复制validator，不省略后续操作。正常后续推进仍须返回原受理事实，不能以当前base重新受理。
- 已报告；若作者提出只atomic需此闭包，须先由根明确改变已批范围，不能静默减料。最终处置待补。

### P2-04：完整行允许标量不等于逐列 SQL 类型核验

位置：`_MeteredGate._cost`。其仅统一允许text/integer/null，未按固定schema列限制typeof；未被后续semantic helper使用的列因此可带错类型通过。

真实成功test.read后fixture将`job_results.created`（INTEGER列）改为TEXT `wrong-sql-type`并恢复triggers；C2仍返回job-record。费用核同没有识别类型损坏。

- 命令：`.venv/bin/python /tmp/t01-c2-independent-result-type-probe.py`。
- 完整工具结果：chunk `19ae1d`，exit0，输入源码d8c927ee。
- 实际：jobState=succeeded，createdType=text，finding=job-record，unchanged=true，transaction=false。
- 建议：固定每表每列允许SQL typeof集合，明确nullable，在现metadata步骤拒错类型；不修库、不另建schema。加入INTEGER→TEXT及真实nullable阳性反例。
- 已报告，最终修订待补。

## 已核实现结构及剩余审查

已全文核读固定模板、同connection gate、真实unbound方法绑定、classmethod/staticmethod语义、_Cursor错误穿透、完整行计价与seen、selector预量、Job/创建来源及terminal分支。没有发现真实boundmethod回退、第二连接、主动write/reconcile/cache补写或新增公共authority。独立四探针均观察到本次BEGIN/ROLLBACK释放和读取后dump相同；这不代替全部异常或OS故障验证。

另向主线提出预算静态核对点：guard-phase的table names直接fetchall仅预留64行，原schema对象guard允许至256对象，原_preflight在fetch后才判≤64表；name/PRAGMA metadata的可变TEXT与完整schema材料计费边界也应按已批§5明确。尚未以此条独立重复计P2，待主线处置和实际证据。

最终模块/测试/说明hash、必要定点复测、主线正常check/source终态和54项候选身份尚待追加。本审查不能代替指定GLM-5.3/M3.1-Flash同版双审、CI、正式Host/物理dispatch/current-scope或父FR验收。

## 后续独立组合故障观察

输入源码37454B/SHA256 `d332c6156ba7b58fe6aa2cdbac5948ad7c5ad3309e6ae591056a8a1522b8ac95`：在真实临时JobStore连接，以受控 `_catalog` 抛 `KeyboardInterrupt`，同时受控driver令ROLLBACK抛SQLITE_IOERR。实际收到原KeyboardInterrupt，cleanup_failed/context/cause均无，owner连接仍in_transaction=True。当前finally保留了取消首因，但未把同时存在的cleanup失败以有限信号交owner。

命令 `.venv/bin/python /tmp/t01-c2-independent-cancel-cleanup-probe.py`，完整结果chunk `66e454` exit0；脚本finally关闭注错并手动rollback/close，不遗留临时事务。此为受控driver和取消机制反例，不是OS磁盘故障证据。建议保存BaseException原对象，清理失败后仍抛原取消并附有限cleanup状态或明确可信carrier；不可改为吞取消的incomplete。已发主线，处置待补。

## 继承身份独立读回

工具chunk `2ba076` exit0：实际控制manifest14521B/SHA256 `aef7b7c2d61cadb0eb8de73b5697f7ce78d384d217ff301bacd9038ff291f9cd`，逐52条比较当前bytes/SHA与其指定423b原Git字节，全部完全相同，无失败。AGENTS相对5f的修改是批准保护规则的当前78df字节，未由本审查者修改。此读回不代表新两个writer最终冻结，也不是运行验收。

## 修订1c5d8e08定点复核

主线read-ready模块39711B/SHA256 `1c5d8e08fc960f051bd1ba39934fec3c030312587d8c725ecd6a4ffa51777f37`。独立工具 `81175d` 核起始hash并全文读取前440行，`dc98f1` 完成余部；同版原五脚本实际重验，结束 `024a89` bytes/SHA完全相同。非冻结测试尚不纳入final。

| 原问题             | 修后实际完整工具结果（全部exit0）                                                                       | 结论                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| P2-01 header       | `430c00`：actual3正常job-record，0/2/4均state；每次headerQueried=true、dump不变、事务释放               | 定点关闭                                     |
| P2-02 float        | `70c5ef`：原合法三小数成功Job返回job-record，dump不变、事务释放                                         | 定点关闭；selector与SQL计量未放宽            |
| P2-03 fullhistory  | `42e150`：同一坏当前CP改报incomplete，trace确有app_checkpoints读取；原history仍拒绝，dump不变、事务释放 | 定点关闭                                     |
| P2-04 typed column | `fc790b`：createdType=text改报incomplete，dump不变、事务释放                                            | 定点关闭；nullable仍沿原SQL，而非擅增NOTNULL |
| 取消+cleanup       | `56be32`：原KeyboardInterrupt保留且cleanupFailed=true，transaction=true真实报告；脚本finally手动清理    | 定点关闭；仍为受控机制故障                   |

新增guard已实际改为table count≤64后定位/收费schema完整行再返回name，table_info count≤32后读取，schema/metadata重复读取工作继续计数；固定三个工作常量未放大。新增路径仍发现以下有限异常遗漏。

### P2-05：schema预收费结构异常在有限映射之外

同一1c5d8e08模块，真实已开临时Store3，仅fixture用writable_schema给jobs对应sqlite_master.sql追加NUL后立即关闭writable_schema。新preflight→_schema_fee→_cost的_require抛ValueError，入口内层结构异常catch尚未覆盖该阶段；外层BaseException原样重抛，因此私有调用者得到ValueError、reason=None，而非批准的有限fault/事实union。

- 命令：`.venv/bin/python /tmp/t01-c2-independent-schema-fault-probe.py`。
- 完整工具结果：`f574f8` exit0；exception=ValueError，reason=null，message="Incomplete operation evidence"，unchanged=true，transaction=false。
- 这是受控持久schema损坏反例，不是合法DDL或OS故障。它证明异常合同漏口，不表明读取有写入或资源泄漏。
- 建议：新预收费阶段已知结构异常也按批准合同有限映射；保持EvidenceFault/HostReadFault资源与存储语义，真正BaseException取消继续保原对象，不能用泛catch把取消变成incomplete。
- 已向主线即时报告；等待下一固定delta闭环，故本报告尚不判最终通过。

新guard先界另有独立真实机制补证：`.venv/bin/python /tmp/t01-c2-independent-schema-bounds-probe.py`，工具`af9b9a` exit0，输入同一39711B/1c5d8e08。自有临时库扩65表时resource-limit，原SELECT name未物化；另一库把jobs扩33列时resource-limit，原PRAGMA table_info("jobs")未物化。两者dump不变、txnFalse、末ROLLBACK。此为非法结构fixture的拒绝顺序证明，不算正常schema阳性；前述guard表列前界静态观察在该版本关闭。

测试作者read-ready48970B/SHA256 `6a543d4300fe3d066a51d10562120e7eac82d73022a8e32f601329e34d6e9c03`，独立工具`4e52b8`/`f7f75c`已实际核新增后半源码与身份：真实ChangeSet完整分页确认/末段与detail损坏/后续base、partial failed/cancelled、反向round关系以及消费blob自hash但config/params错配均有对应原writer材料。作者报告127项通过不等于独审者重跑；P2-05后新测试/终态仍待最终绑定。

原三份修前模块由主线按其原patch/ruff反向恢复后存为revisions/*.py.txt；独立只读工具`7dc651` exit0逐核36821B/3bf、36998B/d8、37454B/d332均与原探针打印SHA完全一致。本审查未执行这些恢复副本，未将其说成探针当时即时副本。

P2-05同类容器异常补证：独立脚本`.venv/bin/python /tmp/t01-c2-independent-context-shape-probe.py`，工具`3534a0` exit0，实际输入39771B/SHA256 `1ce644112d016212903aafa684a531253396f1932683efd1d38639d14397b228`（主线开始下一修订，非前述冻结1c5d）。自有临时Job将context.manifests改为[]，用原digest同步jobs/claim fingerprint并恢复triggers；_job调用.items()抛原AttributeError、reason=None，dump不变且事务释放。这是坏shape但hash自洽的结构反例，并未认证原授权。已请主线在同项内明确容器使用边界或其余Exception有限映射，同时保留独立EvidenceFault、存储/资源及真正BaseException取消语义；不另固定审查轮数。

## 最终代码候选及P2-05闭环

| 最终材料                                                           | bytes | SHA256                                                             |
| ------------------------------------------------------------------ | ----: | ------------------------------------------------------------------ |
| packages/engine/src/ontolearn_engine/project/operation_evidence.py | 39943 | `d6554289f8263a09216b76ff9d18e7b38aef81730f2c029669f816a7c6a5b2ae` |
| packages/engine/tests/test_project_operation_evidence.py           | 50985 | `9097ccb758c4f05786923277b34c33960e716c63bd8f5eea464d850dbcf09a76` |
| docs/iterations/T01/project-operation-evidence-core-C2.md          |  5310 | `7b78c8c8376d238c51d21e65b1e066f11375ed86c1adbce22245be98b00db4f5` |

独立工具`ee99e1`实际核上述起始身份，读manifest显式dict检查、同一结构catch内的guard preflight、HostReadFault显式穿透以及AttributeError/IndexError结构族；同时完整读两个新增测试。两个fixture分别是原schema SQL追加NUL、原context manifests=[]后用原digest同步实际jobs/claim fingerprint，均未以删断言或假数据绕开关系检查。

- 原schema脚本修后工具`8663ef` exit0：source39943/d655，finding=incomplete-evidence、unchanged=true、transaction=false。
- 原context脚本修后工具`6b93c6` exit0：同版source39943/d655，finding=incomplete-evidence、unchanged=true、transaction=false。
- 结束工具`84ece9` exit0：module39943/d655和test50985/9097均与起始完全相同。

P2-05在此版本关闭。修订只扩充已知结构异常有限映射，EvidenceFault不继承被捕获族，HostReadFault显式保留外层资源/state映射，门的SQLite错误分类及真正BaseException取消首因路径保留。没有重新运行原四项无变化矩阵；其1c5d的独立实证和本次最小delta分别记录，不倒称早期通过已覆盖所有新字节。

主线报告此版新增专项129 passed/6.39s（dbfefa）、ruff通过（62d1e1），独审未重复作者矩阵。新正常fullcheck02的session75525在本次代码收口时仍进行中；check01旧1c5d实际通过仅属被替代候选证据，不能覆盖最终d655。source独立实际终态待主线提供后只补证据绑定，不重测无变化代码。

最终独审意见：当前授权范围内未发现未解实质问题，支持本内部C2候选进入后续同版门禁。该结论涵盖有限selector、同连接/本次事务生命周期、完整typed行预扣及传递查询门、目标history、真实受理/来源/terminal/result/rounds关系和有限异常；它是基于所读代码、原实现与已列真实小探针的审查意见，不是数学穷尽证明或CPU/RSS/容量保证。

仍保留正式原dispatch/物理绑定与current-scope、真实profile/frame/envelope、公共路由/Host首IO、启动和preview既有预算风险、普通Job origin未记录、场景领域语义、指定GLM-5.3最高/M3.1-Flash xhigh同版双审、CI/PR/正常develop合并、双OS/真人及父FR/57P0门。没有GUI、native、e2e、模型、网络、打包或推送合并证据。

## 最后同版运行证据绑定与冻结

主线提供最终normal check02真实终态：开始`526574`/session75525，终态`31c3d7` exit0。独审只读核原日志`/tmp/t01-operation-evidence-core-check-02.log`，8914B/SHA256 `e00da643e9a58de34a097eb88e18da9d3ee0791d3778b891e42ad2c5fc7f5f0c`；实际pipeline包含lint、显式格式检查、contracts/unit/desktop类型、22文件1125 Vitest、production build、ruff check/format与pytest，终态3098 passed/44原skip、92.87s。原check01仍仅旧候选证据，未倒称覆盖最终版。

独立source01主线工具`0b58a2` exit0；独审读`/tmp/t01-operation-evidence-core-source-01.log`，111B/SHA256 `1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536`，实际核12原归档源。独审原件读取工具`dff606`/`093666`及后续中段读取只做文件核验，未重新运行全仓或产品。

同一读取再次核当前module39943B/d655与test50985B/9097原字节未变。至此，本报告此前“check02/source待补”均作为当时历史状态保留，当前最终意见所需本地正常检查与来源证据已绑定，无未解独审阻断。结论仍限本内部C2私有读取阶段；指定双外审和正式生产/父FR门不因本报告关闭。

本报告完成后冻结；审查者转任其他独立新树的实施作者，不再修改C2报告或C2产品/测试。后续阶段须由另一位独立审查者审查，不能把本次独审身份延伸为对自己新实现的独审。
