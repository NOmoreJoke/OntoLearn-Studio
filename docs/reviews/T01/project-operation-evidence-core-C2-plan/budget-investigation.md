# C2 原操作证据核心：独立预算调查

结论：可以在原已打开的真实连接上实现有限只读证据核心，但不能直接给 `_accepted_job` 外层加一个字节计数器就宣称完成。必须冻结完整 typed SQL 行的 canonical UTF-8 计价、对所有传递读取生效的同连接查询门、按实际行身份去重及完整引用闭包；另保独立 SQL 工作 guard。现有启动校验没有本次 maxEvidenceBytes 保护，且原 `_accepted_job` 没有完整 terminal receipt 互证，均须如实列为现状。

本轮只有方案准备，没有 C2 产品写权。以下均为调查/拟实现方案和未来验收，未执行产品、SQLite、测试、构建、网络、模型或 GUI；只写本报告，不修改 C1/旧 docs。内部核心只能证明“当前已打开库中存在什么证据”，不能输出正式 resolved、造 scope/物理 capability 或关闭原意图 unknown。

## 1. 实际依据与源码身份

全文读取根 `T01-operation-evidence-C2-plan-preparation.md`：4190B / SHA256 `3a2fb6b04154bdc29fcda1d92c74cfe7c5e8438950ae55c7b49dd573d05d9195`，工具 `b9b6e6`。固定合同 `379916267e5c36eebedb44d35a6636b9915ccd70:docs/iterations/T01/project-create-and-resolution-contract.md`：39602B / `ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3`，实际读§3/6/7/8/9。`45141c` 输出包装截断了§7尾/§8，已用 `12ef64` 精确补读209–242行，未把截断当全文。AGENTS仍15852B / `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，沿已读规则。

调查树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-create-core`；实际HEAD `a33cc80e82475e54d74b4e48c1fd32f32979983a`，产品固定ref `423b7e4c799f188cf2ce6e8e7121893ce85624cd`。`70c1b2` 对以下四个核心文件逐 Git/current bytes核同，其余项为同次调查的真实现文件；本报告不替代59件冻结清单的另一独立核对。工作树 AGENTS 为既有修改，未触碰。

| 路径（packages/engine/src/ontolearn_engine/下） | bytes | SHA256                                                           |
| ----------------------------------------------- | ----: | ---------------------------------------------------------------- |
| job_store.py                                    | 87227 | 8896c3e30007e1dec04eaf47ae5bb5c33a1e9b3a1d016cb9165f99d8b4deeacc |
| project/format3.py                              | 32169 | 505d0beb124534b2ab2e6c1716df53ef7b8108bedb57f5300fcb79a68e955782 |
| project/project_host.py                         | 15777 | a142d9dc9e3c56c51110fd21125c65cc72a19631743be92ccf2e8be98da4edeb |
| project/project_lifecycle.py                    | 20932 | a43365c1615082a0229de0d8e48569227fa930a7c3a7f869360975d72f30d104 |
| storage.py                                      | 76042 | fbef0d0ace0a01b9ced5eaecaf83aeb9306258c0cbfa5fd98a6d79e46bc5a39a |
| project/domain_changesets.py                    | 34728 | e38f9d58a31f3bb38dc7b2da58f3da26811d3a6cfcc2a5f43a5a10f9b71dfb9a |
| project/applications.py                         | 20012 | 888bac463c27156a012e08ebfe1df33769a2405c117174611b82a63576a8d90f |
| project/transactions.py                         | 11924 | 13a9f9a104e2f7d0d71ba4b7f66a7adfb40e32631d6d67a9dbd5835ae590a123 |

关键读取工具：`12ef64`、`705978`、`bfacbf`、`be999f`、`88f7c0`、`fa81df`、`8b4f46`、`70c1b2`。仅stdlib静态算式为 `5d7d67`。

## 2. 精确计价：先冻结“完整实际行”而不是另造业务材料

建议主方案冻结 `charge(table,row) = len(canonical({全部固定列名:原SQL typed值}).encode('utf-8'))`。当前所涉固定表有效标量是 TEXT/INTEGER/NULL；TEXT包括 payload/context/dto 原字符串，保留空白与转义，不先 parse、删字段、规范化成另一份 DTO 再计费。该临时计价对象不是新业务 context、持久账本或公共返回。表名/列集合由固定 schema 白名单给出，不能由用户SQL或任意表结构自行扩张。

对有m个列的完整行：

```text
charge(row) = 2 + max(m-1,0) + m + ΣL(columnName) + ΣL(actualValue)
L(NULL)=4
L(INTEGER)=十进制表示的字符数（包含负号）
L(TEXT)=2 + Σ每个Unicode scalar在canonical JSON字符串中的UTF-8编码长度
```

每字符计费为：双引号/反斜杠和短转义 backspace/tab/newline/formfeed/carriage-return各2B；其余U+0000..001F是6B；其他scalar按1/2/3/4 UTF-8字节。实际NUL或非法scalar按合同有限结构/输入失败，不静默替换。引用字符串出现在context和单独blob行是两处实际持久材料，两行各计；同一snapshot被多处引用只计其真实行一次。

`reader._preflight` 的 CAST BLOB总额是原全库结构/工作政策，不能当这个canonical UTF-8额度：数据库UTF-16会改变BLOB长度，JSON转义也会改变编码。不得因普通Store默认建UTF-8而假定所有获准同schema库编码相同。SQL NULL也不能按旧BLOB口径0B计本canonical行的4B。

### 2.1 SQL先界再读的可行probe

每个payload读取前，SQL先返回有限row locator、typeof、TEXT字符数/原存储字节数及必要的NUL/类型检查、完整行的精确canonical费用；不把TEXT参数传Python UDF后再计价。Python只在当前行或结果集合累计费用不超过剩余额度后取得其全部实际列。随后独立计算同一canonical行长度核同，若不一致整体有限失败，不继续验证或返回充分证据。

精确TEXT长度有两条实现路径：

1. 实核 `PRAGMA encoding` 为UTF-8时，令 `u=length(CAST(t AS BLOB))`，`N(c)=length(t)-length(replace(t,char(c),''))`，则 `L(t)=2+u+N(34)+N(92)+Σ短转义控制字符N(c)+5*Σ其他1..31控制字符N(c)`。先拒实际NUL；该式包括所有转义扩张，固定次数SQL内建扫描，不依赖JSON1序列化与Python canonical恰好同字节。SQLite只返回最终数值。
2. 编码不是UTF-8时，不默许当UTF-8或无授权拒整个合法库。portable probe可在SQL用 `unicode(substr(t,i,1))` 枚举scalar，按上式字符成本求和；它不把整TEXT搬进Python。非法SQL TEXT/无法解码时有限结构失败，不替换后冒称相同证据。

第二条可能有O(n²)扫描，64MiB字节限并不证明CPU可接受。必须先只取每TEXT的n并做保守工作guard，之后才执行逐字符probe。例如把 `Σ(n+1)² <= maxProbeWork` 冻结为独立有限工程额度；候选上界536870912个抽象字符访问单位仅供主方案明确批准，不是实测毫秒结论，不应私下复用某个同值常量混成字节预算。百万字符在此工作guard前就拒绝，不能先完成10^12量级扫描再检查。UTF-8固定replace路径同样应按固定扫描次数×原字节总额预检，并由有限SQLite progress opcode额度兜底；callback由可信连接owner管理、组合和恢复，不能覆盖未知原callback后假装可恢复。

maxEvidenceBytes与maxProbeWork/opcode/结构行数是不同guard。任何一个超限整体resource-limit，不截断；这些工程上界不声称RSS/耗时已测量。probe在SQLite内部处理大值也可能分配内存，所以要保留原全库raw字节/行数/schema和工作guard，不能只证明“未搬Python”就声称整个进程内存安全。若portable SQL probe实现无法证明精确且有界，应先申请明确profile限制或更合适的既有只读hook，不用先读整TEXT的UDF掩盖问题。

### 2.2 实际行身份与去重

一次新读事务中维护仅本次有效的 `(table,实际完整PK)` seen/cache，取完整行后验证PK与查询条件相符。现固定schema均为普通rowid表，可在读PK前先用 `(固定table,rowid)` 作为有限内部locator，SQL先probe该行全部列后才取得可能较大的PK；rowid只作本次事务定位，不持久化、不作为业务身份或跨库证明。不存在的新行只构成缺证，不虚扣一行；出现同主键多行或JOIN倍增为结构失败。

每行只在首次读取/解析之前扣一次；重复helper访问使用相同已核行缓存或确认其属于同一读快照。JOIN如marker必须分别将commits与commit_evidence两条实际行收费，不能用JOIN输出代替实际行集合。不同表/不同项目同ref、不同PK但同payload/hash是不同实际行，各扣一次；一个JSON字串内部重复出现不会被hash去重删减。不要从16条分页、当前缓存、当前目录行猜完整集合。

批量history查询先count及probe全部命中行，在固定全库行数界内分批取有限locator/费用，累计通过后才取完整payload；不先fetchall大PK/大TEXT再算。不得为seen建立临时SQL表或第二连接；全量有界metadata、费用探测不等同已解析证据，可以只保有限定位信息，读取对象总量仍受独立guard。

## 3. 同连接查询门与原validator复用

建议单次调用私有 EvidenceView：它不继承/调用Store构造器，不开库、不替换真实store._db；持有原真实Store及同一真实connection，只读方法明确绑定原JobStore/Store实现到view，view._db指向计费查询门。每条已知SQL模板声明实际来源表/完整列/PK/参数谓词/顺序与投影；先probe和扣实际唯一行、取得缓存，再给原方法返回准确原投影。未知SQL模板或未覆盖自调用立即有限失败，不能回落真实连接“先跑通”。

SQLite authorizer负责拒所有写（INSERT/UPDATE/DELETE、DDL、ATTACH/DETACH、写PRAGMA、SAVEPOINT/隐式写路由等），允许明确的BEGIN/ROLLBACK读事务及所需只读函数/PRAGMA；不是计费器。它只见表/列、不见每行PK，prepare缓存也不是逐读取回调。因此“SQL白名单+authorizer”仍不能代替全传递查询门。测试还应在外部拒全部写的authorizer下运行，证明无写行为；service不能随意覆盖未知caller的authorizer状态。

view不得将 `getattr(realStore,name)` 得到的普通bound读方法直接透传，否则其self._db回到真实连接，绕过计费。需要列出纯函数/staticmethod/classmethod与所有读方法的明确白名单：纯classmethod可沿真实类复用；会查询的方法必须绑定view，所有递归调用继续走view。原hash/shape/plan/history校验不得复制成简化分支，不能给缺方法写返回true/空集stub。gate返回的行必须来自同conn实际读回值，保持原方法索引/keys/dict语义；不是合成受理事实。

若这个view不能严格复用，须逐切点申请readhook：job_store `_accepted_job`1015、`get_job`1080、`_job_prepared_plan`776；还必须让storage `load_snapshot`1225/`_project_snapshot`1234、marker1199、state/vector和format3 `_history`587全部经同一accessor，不能只改顶层三个方法。已有domain_changesets `accepted_plan/_verify_plan/_receipt`与applications `claim_context/check_confirmation`都接受传入store，传严格view即可，不必先扩大这些文件writer。确需修改时另报实际绕门反例和精确路径，不能以“只准两个新文件”为理由复制原validator或隐藏所需改动。

本报告建议的新实现责任可位于专属内部证据模块及专属测试，调用入口由主方案明确申请；不在本报告自行授路径。既有lifecycle/JobStore/format3/storage任何readhook仍须根重新授权。固定只读ref/path/bytes/SHA可直接用第1节，分支/新5f树及完整接收集合由主方案另定，不能沿现C1树直接开始C2产品。

## 4. 必须闭合的完整行/引用集合

| 路径            | SQL先界后读的实际集合与必要核验                                                                                                                                                                                                                                                                                                                                   |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 公共基础        | 精确schema对象/实际format标记（读取SQL正文也先界）、实际public_projects映射、projects；唯一operation_claims，跨项目/kind/knownJob冲突先拒；缺claim不靠marker断言未受理                                                                                                                                                                                            |
| Job原受理       | jobs完整行含dto/context/fingerprint/run；`_accepted_job`核claim和jobs/context哈希、完整expectedRequest+原implementation/limits逐值；inputSnapshotId对应snapshots完整行、parametersHash对应job_blobs完整行；runConfig还要eventsRef、eventConsumptionRef实际blob，即使内容已嵌context仍不能省引用行                                                                 |
| 普通prepared    | job_plans完整payload、job_confirmations完整行；核原base/plan_hash/diff_hash/ref、actor/permission；不把当前base或新确认当原材料                                                                                                                                                                                                                                   |
| 正常ChangeSet   | 同上prepared envelope、完整preview/control before/after/manifest；envelope inputSnapshotId、parametersHash实际行；每个segmentBlobRefs实际job_blobs；confirmationRef对应job_confirmations和job_details完整原确认回执；`_verify_plan/_verify_document/_receipt`严格验证。原host/session从envelope+确认原回执交叉核，而不是传当前host给accepted_plan触发当前base检查 |
| 创建            | application claim完整context、app_format逻辑library证据、真实public映射、app_origins、准确seq1 app_operations/app_receipts和全必要混合history；lifecycle creation_context实际三immutable行核同必须保留，不能只模型自洽                                                                                                                                            |
| 混合history     | 项目app_projects/head、origin、全部app_operations、每个实际app_receipts、原genesis与后续所有app_checkpoints、各domainSnapshotRef实际snapshots、commits+commit_evidence；普通application claim/其prepared+confirmation与draft.restore的原checkpoint引用。最后还读当前域state/vector和app_state对应行，见下文                                                       |
| 当前状态末端    | format3 `_history`会读projects/versions/definitions/facts/mapping_state（以及helper实际用到的retirement控制）和app_projects/app_drafts/app_learning/app_assistance；这些是链末端完整性核验输入，即使不返回也要全部收费。只追before/after两个CP会漏                                                                                                                |
| terminal atomic | 完整Job DTO/claim、marker两实际表、对应app operation/immutable receipt+完整必要链、resultRef对应job_results/results实际行；payload若存在也先界收费并核commit.receipt.v1与marker一致。仅get_job/schema验证不足                                                                                                                                                     |
| rounds          | jobs.run→runs、完整rounds、run_terminal以及初始/各round snapshot、terminal evidence所引event consumption blob；核进度、run/job/project、终态及immutable实际记录相符。run snapshot不是正式domain project snapshot，不误用_project_snapshot拒合法round证据                                                                                                          |

`format3._history`从genesis一直验证到实际当前head，并核总commits集合、receipt/CP集合和当前state/app_state，所以“目标operation以前链”不等于可复用现validator的必要链。后续base已推进时仍要验证原input snapshot；不得重新snapshot写入或用当前state替代原context。共享CP/snapshot会被多次helper引用，只收费一次但每处关系仍验证。

`_accepted_job`返回get_job，它核受理材料与DTO，不完整互证terminal marker/result。新核心应额外按mode和实际终态核：queued/running/cancelling的真实claim即受理，null marker不是未受理；failed/cancelled允许无marker，有marker时按真实记录核，不凭状态补成功；atomic succeeded需要marker/receipt一致；mode none的只读成功不能强求domain marker；rounds用自己的immutable ledger，不拿atomic规则代替。

results.payload可由 `collect_cache`1978置NULL，receipt类型也不例外。不可由cache缺payload否定真实原受理或重新create。atomic历史真实性以immutable app receipt/history+marker及result/job_results归属对应；payload尚在时额外核真实receipt内容，已回收时明确不可重放该cache，不能补写。普通read结果cache回收后，原DTO受理/终态与真实result元数据仍可核，不承诺重建结果正文。若所需immutable proof实际缺失，则内部缺证而非补cache。

普通Job context从create_job915开始固定的字段没有hostClientId/engineSessionId；普通prepared的actor不是完整host/session归因。内部可给真实受理状态和缺来源标志；正式resolution仍origin-not-recorded。即使ChangeSet来源充分，原dispatch物理绑定未交付时正式接口仍unknown/physical-binding-unavailable；复制A→B只证明B里的记录，不能由libraryEvidenceRef、UUID、同hash或当前B许可变成A的物理证明。

## 5. 事务、全库guard和启动未计费风险

入口必须拒未知caller活动事务，明确新BEGIN（读事务）→全部schema/预算/内容校验与结果构造→ROLLBACK释放；失败/取消同样释放，本次不COMMIT任何写。原Store._read402会加入已有事务，因此不能裸调用当充分条件；reader._read142的拒活动事务模式可借鉴。唯一同conn快照内长度probe与读值不发生读前后漂移；不切换连接，不reconcile、不public_project/project_get/snapshot/create/commit。

全库 `ProjectHostReader._preflight`158可沿用原有限schema对象/表/列、所有raw rows/bytes及重复历史work的工程guard；它与新canonical证据累计独立，先跑原guard不意味着目标证据已计费。其只在SQL返回aggregate/有限schema metadata而未解析大payload的部分可不计为payload证据；一旦读取schema SQL/名字等正文参与validator，仍须有限界并按已冻结口径收费，不得把helper暗读包装成“只是全库guard”。

不能在新core直接调用全库 `format3.validate`483或 `_validate_job3`188后才声称只收费目标closure：前者加载所有snapshots、所有项目完整history，后者遍历所有claim/Job并accepted校验。若确实要每次调用，必须把整条全库读取集合也走gate并收费，超额整体失败；更合适的是ready已验证的前提+本次固定schema/全库aggregate guard+目标必要历史验证，不能用ready当本次目标内容免验。

现有启动真实风险：Store.__init__77–96开连接并_migrate，format3._validate501起先load所有snapshot，再验schema及所有项目history；JobStore.__init__46/_migrate_job3已有catalog时即_read→_validate_job3，直接读全claims/jobs/context及其prepared/blob。此过程没有C2 maxEvidenceBytes，也不能由未来在ready之后才进入的gate追溯保护。ChangePreview的完整before/after/diff分配也不是证据字节计费等价于RSS。报告必须保留这些缺口；本阶段不改启动/迁移/宿主，无权宣布已解决。

selector必须先做严格形状、scalar/深度/安全整数、原始Unicode检查及流式有界canonical编码，再复制；maxEvidenceBytes由可信调用者显式正safe integer且≤67108864，不从renderer抬额。selector≤min(262144,真实frame允许大小)；成功投影≤min(131072,真实maxPageBytes,真实frame减实际envelope预算)，不把frame减固定猜值。evidence超限不返回部分充分状态；返回过大也是resource-limit，不分页一个Job/context。事务结束释放本次seen/cache/闭包，不创建游标或长期意图缓存。

## 6. 可复现静态反例与未来验收

工具 `5d7d67`仅import stdlib json/hashlib/pathlib，未import产品或使用数据库：

- 100个ASCII x：原UTF8 100B、canonical字符串102B、UTF16LE 200B；100个汉：UTF8 300B、canonical302B、UTF16LE200B。BLOB长度不能统一当UTF8。
- 100个U+0001：原UTF8 100B而canonical602B；100个双引号canonical202B。预算110时raw长度可过而完整canonical不能过。
- `payload = '{"x":"' + 'x'*100 + '"}'`，parse后的对象canonical108B，原SQL TEXT canonical scalar114B；完整 `{id:'a',payload}` 行135B。只算payload或先parse会漏真实行列与转义。
- 同一行经三个helper读取应只扣135B；另有id=b且payload完全相同的第二行仍135B，总270B。按hash去重会错扣135B，按访问次数又可能扣405B。
- 单个百万字符TEXT满足远小于64MiB，但逐字符substr式最坏扫描可至10^12字符访问；只核bytes不能证明probe工作有界。

未来真实专项应分别测所有整体预算及工作guard的 -1/0/+1，并独立读取真实行canonical参考额，不从meter输出反推；覆盖同ref多次引用只扣一次、不同PK同payload各扣、JOIN两真实行、context内嵌snapshot与实际snapshot两行都扣、segment最后一块/confirmation detail/后续CP/当前app_draft超界时零提前payload读取。损坏reference/hash或缺prepared/detail不能被“费用仍可放入”掩盖。

还需测完整原request/implementation/limits逐字段错配、queued无marker、running/cancelling/all terminal及rounds、knownjob/跨项目冲突、operation定位到第17条以前Job（不走last16）、伪创建claim借domain receipt、原cache回收/当前base推进、A复制B仅本库事实、全写拒authorizer+完整dump不变+trace恰一新读事务+真实重开。计价SQL应核UTF8/UTF16与控制字符/非法scalar、未知查询模板fail closed及原validator所有传递SQL均经gate。以上均为待授权实施/实测，不写Pass。

本调查已将可实现切点、计价歧义、O(n²)工作风险与必要readhook建议发主线。待主线完整方案read-ready后，继续独立预算定点审；本报告不授C2代码写权，不缩小固定合同完整create/resolution及真实binding/首IO/宿主目标。

## 7. 主方案 read-ready 的独立预算定点审

实际全文读取主方案 `docs/iterations/T01/project-operation-evidence-core-C2-plan.md`：33663B / SHA256 `dcebb1e03baac485b06cc22f90611b24503e81c26978695188dcb4b9cf0e7835`，190行，工具 `d7525d`、`7fe0c9`（`12590a`确认361行后无内容）。`9be26c`再次核身份相同。当前是具体方案审查，不是产品实现/DB通过。

整体可行部分：主方案选择本报告完整typed实际行canonical对象；SQL TEXT不先parse、NULL/整数/列名/标点计全；rowid先定位避免先搬大PK；真实同conn原投影、未收费行不先给validator；view不构造Store、不替real._db、不回落真实boundmethod；未知模板fail closed；全closure含ChangeSet全部segment/detail、创建真实三immutable行及当前head全history、当前域/app状态、terminal与rounds分支。全库raw guard与canonical证据额度分开；UTF16不误套BLOB长度；明确无运行Pass、未到progress callback不被声称为时间保障。静态复核相关现函数为 `0a7eb6`、`e7f270`、`ea7fab`、`0a9827`。

本轮未发现view绑定表必须新增的SQL读方法漏项：`_snapshot_state`明确沿原Store类，内部cls._fact/cls._definition仍用原纯validator，不需要假方法；其余能查询的方法绑定view，方法自调用继续走gate。仍应在实施阶段真实覆盖全部模板、staticmethod/classmethod和_db.in_transaction的真实只读属性；本静态结论不能代替实际闭合测试，也不默许未授readhook。

### 7.1 要求明确的计费/工作阶段顺序

主方案§5“先SQL返回typeof、length、存储字节数、NUL、完整行费用数值”有把廉价metadata与完整replace/scanner放入同一SELECT的歧义。UTF16段虽明确先只取n，UTF8段的固定replace也必须先界工作，而不能查询返回费用后才核MAX_PROBE_WORK。

具体静态反例（`9be26c`）：20MiB ASCII TEXT，单按33个N(c)扫描就有692060160单位，大于536870912。若同一SELECT同时返回n/u和完整canonical费用，SQL已完成超额扫描，Python才可能拒绝。该反例不依赖该行最终业务是否合法；损坏/历史超额行同样不应先运行完整昂贵计价。建议冻结分段：

1. 限定实际行数/locator；只取typeof、n、rawbytes与必要NUL等廉价metadata。
2. 对本行所有字段、固定开销及已有probe消耗累计预扣独立工作额度，通过后才运行费用SQL。
3. 完整canonical费用返回后，先核maxEvidenceBytes；通过后才执行正文原投影。
4. 正文实际完整typed行费用核同、解析、扩展引用；重复访问不重复扣证据，仍受实际工作/查询界约束。

UTF8的“固定replace扫描次数”须给明确保守系数与计算式，以便工作±1有独立参考。33是N(c)数量，不自动等于33次完整扫描：每个 `length(t)-length(replace(t,...))` 还可能扫描原t、replace结果及执行replace。不得把含糊的次数称为已证明CPU上界；这些只能是明确定义的抽象工程工作单位，不能冒充时间测量。portable平方公式亦须在执行scanner前按字段预扣，并保持同一工程单位解释。

### 7.2 重复证据免费不等于重复读取没有工作

主方案§4要求原projection仍由真实SQL生成，§5重复行使用已核费用。这可以保证actual-row唯一计价，但不消除实际重复投影/解析：Store._state对M个mapping owner分别调用mapping_status1003，每次再调用vector358；vector重新读definitions/facts/mapping_state/versions等；format3._raw_checkpoint又会对多CP反复load同一snapshot。原reader.validation_work的乘数仅含app_operations与snapshots，不含mapping owner数。

因此“查询次数在有限集合内”应改成明确拒绝界，例如另冻MAX_QUERY_COUNT和每次实际投影的MAX_READ_WORK（重复查询照扣工作，证据额度仍只扣一次），或证明并写出足够保守的同等工作界。不要只用seen集合大小证明重复查询成本已控制，也不必为此冒称时间/RSS保证。后续验收须有同一行重复引用、mapping/vector重复路径和-1/0/+1，证明唯一证据扣费与重复工作扣费互不混淆。这一意见已直接发主线，尚待方案处置。

### 7.3 有界输出编码的具体反例

主方案“不先构造超额完整编码”的约束正确，但普通stdlib `JSONEncoder.iterencode`不保证单chunk有界。工具 `9be26c`仅用stdlib构造200000个U+0001字符串，`next(iterencode(s))`即产生1200002字符/UTF8字节的完整转义字符串块；在调用者检查131072额度前，该大块已经分配。

建议明确字符串scalar必须先按字符计算canonical UTF8长和剩余额度、或真正分块escape/encode；对象/数组迭代器仍要对大key/string生效，不能在拿到stdlib大chunk后才len(chunk.encode())。此项是现有“有界编码”约束的具体实现禁例，不申请另一schema/业务DTO，也不是产品运行测试。

本轮判断：计价与完整闭包设计可实现；上列严格阶段顺序、独立重复工作拒绝界和编码禁例应由主线在方案中明确处置后再冻结最终身份。当前不把本draft记为无条件预算审查通过；C1及已有59原件没有改动，本审只追加本报告。

## 8. 修订40363B方案的预算复核

主线修订方案实际40363B / SHA256 `ff93f5017fefa71630a3c15e6d2f44ab2cebb867e75afbb47f005bcd652e2cbc`，196行；本审以 `f0f664`、`374138`重新全文读取，`72a601`终核身份。以下关闭第7节三项原意见，保留其反例用于实现验收，不删除历史审查记录。

1. 明确A仅metadata、不混完整费用SQL；B预扣全部字段工作；C精确费用与唯一证据累计通过；D才读正文。UTF8每首次TEXT为 `256+160*(u+1)`，portable为 `256+16*(n+1)^2`，NULL/INTEGER每字段64、每行128；所有schema候选TEXT也计。系数已明确是独立工程收费，未称SQLite opcode/耗时/RSS上界，也没有覆盖未知progress callback。
2. 新增MAX_QUERY_COUNT65536，schema/aggregate、metadata、费用、正文和原helper执行都在execute前扣1；MAX_READ_WORK536870912独立累计，每query128+每次实际行全canonical费用，重复照扣。metadata/probe查询在执行前按128+128×固定返回列数×已界行数预留，避免先取结果后查额度。整条批量查询在发正文前先完成行数/费用预扣，cursor分次交付不绕过。证据seen只免重复证据费，没有免实际query/read work。
3. selector深度32、节点≤maxSelectorBytes；key和值的scalar先字符计canonical UTF8额度，再真正分块escape/encode，排序仅在keys已界后执行。200000 U+0001→1200002B iterencode首chunk反例明确纳入禁例与未来矩阵。

工具 `5c8654`仅stdlib算式核：不含其他行/字段固定开销时，单TEXT UTF8费在536870912以内的最大u=3355440，portable最大n=5791；实际还要扣每行128等其他费用，因此不是完整请求必过阈值。20MiB UTF8的预扣费3355443616，百万字符portable预扣费16000032000272，均会在昂贵费用SQL前拒绝。这些是精确政策算式，不是运行性能数字。

完整引用闭包没有因guard细化缩减：原accepted/ChangeSet全部实际材料、当前head混合history和当前state/app_state、result全字段、rounds材料仍经同conn gate。新修订把run=NULL且无progress的合法非成功rounds受理与0轮已开run区分，避免凭缺run拒真实受理；该语义由另一独审负责，本预算审仅确认按实际存在行收费、不造缺失run行。结果依赖/manifests/projection/kind/cache_key及存在payload行的完整校验新增所需实际行均在原closure内，没有引入未经计价的新库/新context。EvidenceControl独立异常穿透旧helper，能保资源失败不被ValueError/SQLite捕获族误报incomplete。

另已向主线补一项收尾边界：如果65536包含所有实际execute而没有为finally的ROLLBACK预留控制槽，最后一条SELECT耗尽额度后，cleanup也会被同guard拒绝，留下活动读事务。应在BEGIN前预留BEGIN/最终ROLLBACK的固定query及read-work额度，或用明确计入总体的独立两控制槽；资源拒绝不能阻断已开启事务的ROLLBACK。未来±1/额度耗尽测试应核in_transaction=False，且不回滚caller原事务。该项不要求新产品路径或改变业务计费，仅明确已有“finally释放”的资源约束。

当前修订的三项预算计价/工作/编码意见已关闭；最终预算审结论待上述控制槽收尾规则的主线明确处置并核最终文档身份。没有执行产品/DB/测试，所有矩阵仍为待批准验收，不写Pass。

## 9. 最终cleanup增量复核与预算方案审查关闭

主线最终方案实际41960B / SHA256 `1724a6e6c9fd315a7065696720ce221bc68631aaf6b1d690479d70635eafba56`。工具 `5aa71d`独立读取核验该身份，并定点读最终第106行控制槽规则、第186行生命周期矩阵及关联的BEGIN/ROLLBACK/错误穿透段；本轮仅核第8节所留唯一cleanup增量，没有重跑产品或数据库。

已明确MAX_QUERY_COUNT65536总额在开事务前保留BEGIN、最终ROLLBACK各1槽，业务/探测SELECT最多65534次；finally的ROLLBACK走固定独立控制路径，不受耗尽的业务门、证据/probe/read-work或未知模板guard阻断，两个槽仍计总额且不构成无限通道。BEGIN未成功且没有本次事务时不伪ROLLBACK；本次已开始时所有失败/取消都尝试实际释放。真实cleanup失败保首因、向owner标清存储失败，不声称连接已清理。矩阵已要求业务额度恰耗尽/±1拒绝仍执行保留ROLLBACK并核in_transaction=False，不回滚caller事务。

第8节剩余cleanup意见因此关闭。最终预算方案结论：对上述41960B固定候选，完整typed实际行canonical计费、SQL metadata→工作预扣→精确费用→证据预扣→正文的顺序、全部引用闭包、唯一证据与重复query/read工作分账、有界输出编码及资源失败清理均有具体可实施约束，无未解决预算方案实质问题。本结论是文档方案静态审查通过，不是C2代码实现/运行验收，不授两新writer或任何既有路径写权；查询门实闭合、UTF8/UTF16计价与全部±1/零写/生命周期仍待正式授权后的真实测试。原启动未计费风险与physical binding/current_scope/正式resolved等边界保持不变。

本报告在本节终核后冻结，不再改动；后续实施审查应使用另获授权的新原件，不能倒写本次方案审查证据。

## 10. rounds反向结构引用的最终增量补审

依据本次明确补审通知，仅定点读取新增段与矩阵，不重读全稿或重跑产品/DB/测试。主方案新身份为42685B / SHA256 `e7db89cb52cc75707d0e7a00e637e97701bea7e7d49f623ef464cb1baf44b96b`，工具 `db96f4`实际核验，并读取§6第128行及§10第184行相关增量。第9节41960B结论保留为其对应候选的历史证据；本节是新候选的补充审查，不倒写旧结论。

增量反例成立：jobs.run=NULL而存在rounds.job=该Job时，仅从jobs.run正向遍历会漏掉实际结构矛盾。修订明确无论jobs.run是否NULL，先对 `rounds WHERE job=实际JobId` 定位并按完整实际行收费后读取，逐行核run=jobs.run；NULL应为空，非NULL不得有同Job跨run。随后对真实run的全部rounds反核每行job归属。该反向查询是本次证据闭包的必要补充，不要求扫描run_terminal的无结构关联JSON来猜归属。

预算上只是同一固定表增加一次有结构谓词的查询，仍使用同conn gate的metadata/work预扣、完整typed行canonical证据收费和query/read工作界；没有索引的扫描仍受原全库raw行/字节guard，不能声称性能已测。同一实际round经job反查和run正查重复命中，证据seen只扣一次，实际两次查询与投影工作分别扣；空反查集合不虚扣行，也不省该SQL的query/read固定费用。未新增表、索引、字节口径或预算政策，新增结构集合不产生新的预算缺口。

最终预算方案结论更新为：对上述42685B固定候选，无未解决预算方案实质问题；原静态审查/未运行及正式授权、startup未计费、physical-binding/current_scope/正式resolved边界全部继续。此报告补充后再次冻结，后续不得据此伪称C2已实施或已运行验收。
