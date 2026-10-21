# T01 C1 内部创建事务：独立审查

结论：本报告绑定的最终五文件、实施说明与检查原件在本次内部事务/namespace/兼容审查范围内通过；P2-C1-01 已修复并独立关闭，无本审未解决问题。预算算式由另一独审负责；指定双外审、CI、父 FR 和正式服务/真实物理授权等门不由本报告放行。以下保留初始核验、首次候选与失败证据。

## 规则与固定身份

本审全文读取新树 AGENTS（15852B，SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`）、共同指令（17891B，`e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`）、正式 C1 授权（8323B，`93528eb38395856af86a76edf9c26822ef406f8a32315282086a509db235d8b5`）和 50 项清单（14299B，`c87fd0a1aca68c9a82ceb8aa142a5d8b6ab974d5e29d17588bd1909d64aa9726`）。初次合并输出的共同指令中段被工具截断，随后单独全文补读，没有把截断输出当全文。完整第九节、指定双审与无桌面约束继续；初始核验阶段没有产品/测试执行或 GUI 操作，后续只执行下述自有临时 SQLite 定点。

实际树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-create-core`，分支 `feature/weekly-t01-project-create-core`。采纳 HEAD `ba2c6c293f9fd9e1742c9ab352dae5e3c951f6a4`，parent 恰批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。独立工具原件 `8bb139` exit0 逐 50 项核 current bytes = adoption Git blob = 固定 a816 Git blob，且 bytes/SHA 符合清单；adoption delta 恰这 50 路径、47 项 futureRole readonly。核验时 git status 仅 AGENTS 保护改动。清单全文补读原件 `bb1230`；不 whole-commit 采用，不转移旧测试维护权。

本审仅可写本报告；产品与新测试均由主线唯一编写。正式实施限 `project/project_lifecycle.py`、`storage.py`、`job_store.py`、`project/format3.py` 及新 `test_project_create_contract.py`；其余 47 初始输入只读。没有改代码、测试、依赖、其他报告或旧树，没有 stage/commit/切分支，也没有借其他树环境。

## 既有切点与待验条件

固定 ba2 源的 `Store._transaction/commit`、`format3.seed_project/checkpoint/_raw_checkpoint/_history`、`JobStore._validate_job3/apply_application`、`applications.claim_context` 关键段已直接读（`d5cea8` exit0），以下是实施预防条件，不是已复现的新代码问题：

1. `_transaction` 既有活动事务时只做 savepoint，release 不等于外层 COMMIT。新增路径若返回持久成功必须拒绝未知 caller 事务，或准确限定内部结果；不能发布尚未持久的 receipt，也不能误回滚调用方事务。
2. `creation` 必须与旧 application、任何显式 edit 参数（含空列表）严格互斥；其省略时保持旧 plan/hash 字节和格式2行为。
3. 既有 seed 调用 snapshot/checkpoint 有 INSERT OR IGNORE。新创建路径必须拒绝冲突/坏旧行并真实逐值读回，不能靠忽略冲突修补或接管；旧默认 seed 的行为和 hash 仍保留。
4. 新 creation 历史 validator 应只校当前遍历已持有的 origin/before/after 与完整 claim，不回调 `_history/receipt_for` 或 Job-ready 造成循环。完整账本权威仍由唯一 history 遍历建立。
5. 旧 apply 原 claim 重试在 kind/project 相同时直接进旧 claim_context，遇创建 namespace 应先 identity-conflict；新旧混 tag 仍严格拒绝，不能宽松 fallback。
6. 新分支应核实际 header3、完整 Job3 schema/catalog/claim 结构；只有 Store3 或配置 target3 时写前拒绝，不能建表或假 ready。
7. 写前预算需覆盖完整 metadata、全库候选行/SQL bytes/work、目录快照/所有有效 page_size/offset 及全部合法 editor 的 missing-draft 最坏编码。候选 hash 只是预算模型，真实 genesis 后才作为持久证据；写后不相符整体回滚。不能修改 reader 放宽或调用会拒绝 writer 事务的读取服务。

以上为 read-ready 前预防条件；后续实审和最终身份见下文，保留首次失败。本内部机制不代表正式 scope/dispatch binding/真实位置 IO、公开 create/resolution、宿主接线、父 FR 或指定双外审/CI/发布完成。

## 首次 read-ready 实审

主线给定并独立核同的五输入如下（`330734` exit0）；所有47只读输入同时逐bytes/SHA复核无漂移。独立环境由主线通知可用，本审不借用别树环境。

| 文件                            | bytes | SHA256                                                           |
| ------------------------------- | ----: | ---------------------------------------------------------------- |
| project/project_lifecycle.py    | 20246 | a998ecabd3942e0f271545c105fa1216e66c49ea71d9079523a817241979c3c5 |
| storage.py                      | 76042 | fbef0d0ace0a01b9ced5eaecaf83aeb9306258c0cbfa5fd98a6d79e46bc5a39a |
| job_store.py                    | 87041 | aaa926a277f9da5634796bcb9fb42201020acc89e7801962d770a63e0ffa57fe |
| project/format3.py              | 32169 | 505d0beb124534b2ab2e6c1716df53ef7b8108bedb57f5300fcb79a68e955782 |
| test_project_create_contract.py | 25875 | 78de84517c909fde218821378f424bc1ef515cb296d32ac00a602b9ece675df1 |

实际全文读完525行新模块、724行新测试、三既有修改的完整diff（`330734/ce2fce/12367a`）。预算算式由另一独审负责，本审不重复该专项。主线126目标用例及旧专项结果是其运行证据，尚未当本审最终全套通过。

### [P2-C1-01] Job-ready没有把创建claim绑定到实际创建receipt

状态：首次候选已独立复现；最终候选已修复并由下述独立反例关闭。以下原因描述绑定首次 read-ready 身份。`JobStore._validate_job3`新application分派仅核 `creation_context` 成功，随后调用 `receipt_for` 但不核返回值等于新namespace预期的创建receipt。`creation_context`核精确context/model及公开映射，尚不要求模型中的创建afterCheckpoint或真实创建效果存在。因此同operation只要有一条合法domain历史receipt，就可能被当成完整创建claim的充分历史。

独立原件`4f7fc8` exit0，使用本树独立`.venv`和真实临时JobStore3，未改源码/测试：

1. 通过旧`create_project(UUID)`建立正常空项目；用同项目`commit(op,definitions=[])`建立正常domain操作。此前完整Store/Job验证通过。
2. 仅在受控损坏fixture中INSERT一条`model(project, blankRequest, origin, library)`生成的创建namespace claim（不是运行正式创建服务）。项目/operation/FK/context/fingerprint自洽，但没有对应创建效果。
3. `_validate_job3`与`format3.validate`均接受。实际receipt的operationKind是domain、metadataVersion0/domainRevision1，候选创建afterCheckpoint根本不存在。
4. 完整dump在验证前后保持相同；关闭后真实JobStore3重开仍接受actual format3。工具前后五源码SHA完全相同，绑定上表read-ready身份。

影响：不完整或错kind的创建证据可通过新增namespace的Job-ready验证，违反创建claim必须与唯一seq1/metadata1/genesis→create效果和receipt互证的要求。反例是损坏证据验证，不声称正常创建writer已产生该状态，也不声称客户端或真实位置授权被绕过。

最小修复方向：新namespace路径必须把真实receipt/创建transition与严格模型核同，再认可Job-ready；可在本授权newmodule或job_store分派内完成，不放宽旧application分支，不递归调用history。修复后的回归应包括真实已有domain操作附着创建claim的反例、零修复/重开拒绝，且保正常创建后续历史推进与幂等。

除本项外，已读实现的单外层事务、未知caller事务写前拒、五分支互斥、strict seed避免INSERT OR IGNORE、真实genesis后据实重建context、旧namespace保原validator及旧reader安全拒绝的切点与授权一致。此为首次候选静态观察；后续 P2 关闭与最终检查、实施文档绑定见下文。

## 最终修复身份与独立关闭

最终五文件已独立逐 bytes/SHA 核同（修复静态核验 `ee314e/d2ac93`，最终 `c53f84` exit0）。主线的实现修改停在此身份，本审定点前后再核五 SHA 均不变。

| 文件                            | bytes | SHA256                                                           |
| ------------------------------- | ----: | ---------------------------------------------------------------- |
| project/project_lifecycle.py    | 20932 | a43365c1615082a0229de0d8e48569227fa930a7c3a7f869360975d72f30d104 |
| storage.py                      | 76042 | fbef0d0ace0a01b9ced5eaecaf83aeb9306258c0cbfa5fd98a6d79e46bc5a39a |
| job_store.py                    | 87227 | 8896c3e30007e1dec04eaf47ae5bb5c33a1e9b3a1d016cb9165f99d8b4deeacc |
| project/format3.py              | 32169 | 505d0beb124534b2ab2e6c1716df53ef7b8108bedb57f5300fcb79a68e955782 |
| test_project_create_contract.py | 27843 | de02dcf022da0784e2d5d31dc0d29f8b2ca5cf0691cd2ca19835cd136c91020a |

`creation_context` 现直接将实际 `app_origins/app_operations/app_receipts` 查询的 typed tuple 与候选精确核同，没有调用 history。Job-ready 又把唯一 history 返回的 receipt 与创建 receipt 精确核同。旧 namespace 仍走原 validator。UUID parser 前另有精确36字符边界，避免超长伪 ID 进入解析器；其新增用例属于本授权新测试。

独立修后原件 `a29141` actual exit0，使用本树独立 `.venv` 和自有临时 SQLite，无源码/测试改动：

1. 重放 `4f7fc8` 同一反例：真实旧空项目、真实合法 domain receipt、只附自洽创建 claim，预期创建 afterCheckpoint 不存在。受控只读 authorizer 下 `creation_context` 以 `CreationFault:structure` 拒绝，Job-ready 以 `Format3Fault:Invalid project structure` 拒绝；所有 INSERT/UPDATE/DELETE/DDL 写尝试为 `[]`，完整逻辑 dump 不变。
2. 关闭后真实 JobStore3 重开同样 `Format3Fault` 拒绝；直接 SQLite iterdump 再核无变化，没有零修复以外的副作用。
3. 在另一个真实临时库经 Store.commit 新分支成功创建，再做正常旧 metadata/domain 操作；原创建 request/origin 精确重试返回原结果且 dump 不变。完整 format3/Job3 验证、真实重开、重开后原请求重试均成功。ProjectHostReader workspace 为 operationSequence3 / metadataVersion2 / domainRevision1，原创建 receipt 稳定。此证明修复没有要求项目保持空白或递归 history。

因此 P2-C1-01 关闭。此处只读拒绝指创建 namespace validator 和 Job-ready：普通 format3 的纯领域 history 不单独承担 Job3 全局 claim 完整性，不把其单独接受合法 domain 链误报为该修复失败，也没有为此修改47只读输入。

## 最终检查原件与结论边界

实施说明 `docs/iterations/T01/project-create-core-C1.md` 已全文实读（`277a64`），最终 **10867B / SHA256 `13bcacbd9e3031effe8827856215183a2def15ef2209df175b44a2985a8b6305`**；其私有调用、单外层事务、严格分派、真实 genesis 后建 context、旧 reader 拒绝和未授权边界与当前实现相符。`c53f84` exit0 再独立核采纳50项 adoption Git = 固定 a816 Git/bytes/SHA、实际 HEAD/parent、47项 readonly current 全部无漂移。

本审没有运行全套。主线提供的独立命令实际终态和本审直接读取并重新 hash 的完整原日志对应如下；日志文件本身不冒充进程 exit，本表 exit 来自主线真实 tool terminal 回报。

| 检查               | 实际进程证据                                       | 本审实读原件 / bytes / SHA256                                                                                         | 结果                                                                     |
| ------------------ | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 最终创建专项06     | start b50a2c / session98989 / terminal53abda exit0 | `/tmp/t01-create-core-target-pytest-06.log` / 180 / f3e954e07c05a2ae600a53f52a9c1334a4579c5ec29cd01bdc435f1ad37d4298  | 128 passed，4.81s                                                        |
| 完整 npm run check | start79a7dd / session96986 / terminal3b62e4 exit0  | `/tmp/t01-create-core-check-01.log` / 8667 / 897bd1596e9f61a55baa2a07531208c9adce8a488f22644bbd723f474a1bc2a7         | lint/format/typecheck/build 通过；1125 TS、2969 Python passed，44旧 skip |
| verify:sources     | 7c9c20 独立 exit0                                  | `/tmp/t01-create-core-verify-sources-01.log` / 111 / 1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536 | 12归档源核对                                                             |

原日志全文实读 `01bab0/443347`，上述全部 hash 独立核验 `c53f84`。专项05首次加入反例时实际 exit1（127 passed/1 failed）：新 fixture 错读 `domainRevision`，正确 receipt 字段是 `domainAfterRevision`。完整失败原件仍在 `/tmp/t01-create-core-target-pytest-05.log`，**1519B / `0bc1fd3bc3ee87aba39010fed683734c28900e5e3ffa2815352641732d4a0aec`**，本审全文实读；修正后06才作为最终专项。更早01的 metadata阈值/旧reader资源缺失失败亦由主线保留，不用中间126目标或1133旧专项冒充最终候选。

本审仅给 C1 内部机制范围结论：已发现 P2 关闭；单外层事务、严格 namespace 与旧兼容切点无待修事项。预算专项结论需绑定另一独审报告。本报告不证明正式 create/resolution、dispatch/scope binding、真实位置首IO、host/RPC或I06能力；没有 GUI/Electron运行/e2e/native/HMR/Keychain/模型、付费调用、push/PR/merge。build 的静态打包成功不等于桌面运行。原指定双外审、CI、双OS真人与父 FR 门继续，不能据此声明完整 Goal 完成。
