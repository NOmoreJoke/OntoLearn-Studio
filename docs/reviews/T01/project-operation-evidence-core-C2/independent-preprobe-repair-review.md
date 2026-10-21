# C2 资源前门修复：独立审查准备

2026-10-22。当前仅完成固定旧版与官方来源源码的静态预读，**尚未收到修后固定候选，未判修复通过**。旧产品256b7f1/过程5b11875的正常实跑与历史独审事实保留；资源前门按根修正重新打开，现不可据旧收件直接采用。本文不覆盖或更改原19044B独审。

审查者未实施C2。当前唯一仓库写入为本文；产品、测试、作者文档、AGENTS、Git/index均不修改。准备阶段未import或执行产品，未打开/执行DB、测试、fixture、构建、GUI/native、网络、模型；未读取正在修改的两writer正文。读取旧实现与测试均使用固定Git blob。当前工作树status确有两writer WIP，仅据status识别并避开，不审WIP也不把作者进行中的实现当事实。

## 1. 已实读输入与身份

树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-operation-evidence-core`。实际静态核对产品parent为adoption `f927f4188fc2d285b405f55ff7ca03f675340af2`，过程parent为产品 `256b7f1f1abd51b7cabfdfe9fd2e5013f4e8cd8c`。base为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。以下SHA均为本次读取实际字节重新算得，非只抄来讯。

| 固定材料 | bytes | SHA256 |
| --- | ---: | --- |
| 本树AGENTS.md | 15852 | 78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759 |
| 根developer-common-instructions.md | 17891 | e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0 |
| 根T01-C2-preprobe-resource-repair-window.md | 2868 | 2c66cff25ca1536ffcd2f1bc847a7403cd083ef0561504933152f708139b0704 |
| 根T01-operation-evidence-C2-root-closure.md（含暂停采用更正） | 3429 | 9d8cf0ef94ee6089878d13b09b640e50a5acf4f6442c95f033077756e87372bd |
| 根T01-controller-operation-evidence-C2-source-prereview.md | 20218 | c61b7608f759a3b8e9926a0d7ed8add9a983035533a8a212a185ae2d7b154ab1 |
| 5b固定主说明project-operation-evidence-core-C2.md | 5672 | 459d3cd2e5f940a4d22bb130a071a2dce128da9a58402d486ffb64d056370204 |
| 5b固定原独审independent-implementation-review.md | 19044 | ac72d0d44192299ede4a735d84300c961dc66a71de52fd1aebfe51ca024f276a |
| 5b固定candidate-manifest.json | 18988 | 8dc32b6b6e6908b0bcc9cd7e722aa55a437083487e239f04c4aff5aa67983b52 |
| 256固定project/operation_evidence.py（全文986行） | 39943 | d6554289f8263a09216b76ff9d18e7b38aef81730f2c029669f816a7c6a5b2ae |
| 256固定tests/test_project_operation_evidence.py（全文1331行） | 50985 | 9097ccb758c4f05786923277b34c33960e716c63bd8f5eea464d850dbcf09a76 |
| 固定project_host.py（ReadLimits、_read、_preflight切点） | 15777 | a142d9dc9e3c56c51110fd21125c65cc72a19631743be92ccf2e8be98da4edeb |
| 固定storage.py（canonical、_read、history切点） | 76042 | fbef0d0ace0a01b9ced5eaecaf83aeb9306258c0cbfa5fd98a6d79e46bc5a39a |
| 固定job_store.py（_accepted_job切点） | 87227 | 8896c3e30007e1dec04eaf47ae5bb5c33a1e9b3a1d016cb9165f99d8b4deeacc |
| 固定format3.py（_schema、_domain_schema切点） | 32169 | 505d0beb124534b2ab2e6c1716df53ef7b8108bedb57f5300fcb79a68e955782 |

54清单逐项取256 Git blob核bytes/SHA，52项readonly-inherited再逐指定423b源Git blob核字节，结果54/54核同、52/52核同、无失败。没有将当前两writer与旧Git比较后误当新固定。AGENTS/common已全文读；前次大输出发生截断的根预审开头已单独补读，旧两writer分段读完。

本次读取原工具返回：控制全文b851bd；规则/closure77255d（公共规则另f1e6f6补全）；根预审b3db4a及626ce7；原主6ffe98；原独审c3bdb9；旧模块410d37/08dd64；旧测试5263e6/50f283/3f2bd6；身份5173dd；54与52核对54a010；原helper6f963e；51模板和parent/status3fe34d。均为静态读取exit0，非产品验证。

## 2. SQLite与CPython静态依据

SQLite文件 `/tmp/t01-primary-s1-sqlite-3500400-source/sqlite3.c`，9282866B/SHA256 `e3f5d6901e7492af4a1fc8c4d745cae84c264942524c3fbfc02b82a5ca8818c8`。其版本宏3.50.4，source ID为 `2025-07-30 19:33:53 4d8adfb30e03f9cf27f800a2c1ba3c48fb4ca1b08b0f5ed59a4d5ecbf45e20a3`。本次重新核本地字节与宏/切点；官网SHA3核验是根提供的已有来源，不冒称本次联网验证或已证明当前运行binary与该C文件完全复现相同。

CPython目录 `/tmp/t01-primary-s1-cpython-31212-source/` 的source-manifest.json为1249B/SHA `aadbe9cdfaa46bc3a593a788e60c581f12d95d85f07632205741223693528b3e`，记tag v3.12.12、commit `4a5632fbf9bf59477c540e3f53fa7cdbeea3e3f5`。本次逐文件hash核同manifest：cursor.c40992B/`3a9121e178dc3e9ae76a818a560fcc09d92d0f842c0a711c70c169dd77d30748`；statement.c5986B/`eee3f2fda3f57f9ec3d2bd38022ee6d03687713911777956a024660b073e17fa`；connection.c78209B/`3f231359af5c4c7c48579015892ee66e22a4136e407be5a830254f3a70c84037`。同版本源码仍不等于运行binary复现证明。

已实读并定位：

- SQLite97272–97562，OP_Column先解析record header，再到P5 overflow shortcut。97374–97377允许物理header至98307B；97415调用sqlite3VdbeMemFromBtreeZeroOffset，85107–85151可能分配amt+1并复制header。逻辑DDL≤32列不证明损坏物理record header≤32项。97354的本页payload≤65536；97502–97517本页TEXT/BLOB值先grow再memcpy，不能因后续P5优化而省掉这条复制账。
- SQLite97527–97547的P5 TYPEOF/BYTELEN优化在overflow分支，不是对全部OP_Column工作免计。115504–115522只在函数参数本身TK_COLUMN/TK_AGG_COLUMN时设置相应P5；`octet_length(CAST(col AS ...))`、拼接等wrapper不能无证明继承直接列性质。
- SQLite130495–130527 lengthFunc对TEXT取UTF8并循环；130622–130689 instrFunc取bytes/text并扫描。bytelengthFunc130532起按值编码选bytes/bytes16，返回的是相应实际字节口径；不能把UTF16物理u直接当UTF8 canonical字节。首次简单metadata必须先付header/local/statement，后续转换/NUL/精确费用扫描再按已界值预留。
- SQLite98073–98093 OP_Count明确精确count访问每一B-tree页；81985–82051 sqlite3BtreeCount按页循环。只返回一个integer、不物化TEXT，不等于固定128单位内已付全count工作。带WHERE/count子查询还需额外证明过滤、索引/表选择与扫描界，不能从结果count反向补首次执行前的费用。
- CPythonstatement.c的sqlite3_prepare_v2发生在执行前；cursor.c875–905附近_query_execute绑定参数后调用stmt_step，故connection.execute并非只建cursor。cursor.c319–435的_fetch_one_row会sqlite3_column_text/bytes并建立Python Unicode/bytes对象。cursor.c1112–1115先构造当前行，再stmt_step下一行，最后才返回本行；fetchone/iterator存在下一行lookahead。准备阶段已将此点通知root。64块策略须预付首step、整块和fetch最后推进，不能只按已经返回的64行追扣，错误步进同样先付。

来源读取工具3382cd/fa727d/80d548/141d43/312c2c/01415b及定位4bea2a/e83bb4/2f84f3，均exit0；没有运行SQLite/CPython构建或SQL EXPLAIN。

## 3. 旧版漏口与历史测试能证明什么

旧模块210–325的_raw只在SQL前预付query和128+128×numericColumns×rows；_cost每列先execute/fetch `typeof,length,length(CAST AS BLOB),instr`，收齐n/u/NUL后才检查并增加probe。u/n本身的获得已经可能扫描/转码/复制巨大TEXT。其后UTF8 replace费用SQL与UTF16递归substr的确在probe预留之后，这一局部顺序不能倒推此前metadata也已预付。

旧project_host._preflight158–196经_guard_query420前后的通道执行schema及全库各表sum(length(CAST(... AS BLOB)))；只按两个返回数字收固定raw费用，TEXT扫描发生在全库bytes/work检查之前。_locators先完整count再SELECT rowid，也有结果数量尚未界定时的查询工作问题；WHERE/ORDER BY可先接触未收费值、索引记录或sorter，不因投影仅rowid而自动安全。

原大TEXT专测只断言没有replace/recursive/SELECT* job_blobs正文，明确允许metadata已执行；因此它证明精确费用SQL前拒绝，没有证明首次扫描前拒绝。原低evidence测试同样只排除SELECT*及SELECT sql正文，不排除metadata扫描。原verify_ledger依据_raw的旧固定公式及_cost记录核账，能核公式递推自洽和完整typed行金额，不能独立证明SQLite隐含工作已覆盖。原129正常/异常结果、dump不变、事务释放记录仍有效；本审未重跑，不否定它们实际发生。

## 4. 新fixed到位后的正式审查清单

当前以下为待审要求，不是已完成证明，也不是给作者新writer或放宽policy。

1. **首次execute前门**：列全入口，包括PRAGMA、schema识别、列数/表数、row enumeration、metadata、feeSQL、guard、原helper正文、BEGIN/ROLLBACK。每次执行前需要一个不依赖该次扫描结果的已付上界。表名、DDL、PRAGMA类型名的缓存填充本身也先付；不把完整巨TEXT先交Python UDF再计费。
2. **物理record与local路径**：用固定SQL源码及真实EXPLAIN支持直接列优化；计物理header98307与本页65536上界、每个实际列取值/游标重启/重复statement的次数。坏schema/record在拒绝之前做过的工作同样收费。不要用logical32或结果scalar小替代物理成本。
3. **有界枚举**：如果使用rowid-only 64 keyset块，检查空表、1/63/64/65、负rowid/最小及最大int64/稀疏rowid，确保首次块可覆盖全部合法rowid，没有`rowid>0`遗漏；界外第1行检测及全库validation_rows累计在下一块/其lookahead前付。保持一次新只读snapshot，不能分批新事务或LIMIT截断历史后假完整。
4. **实际扫描与cache**：逐原51个_TEMPLATES核匹配集合、参数绑定/数量、SQL affinity、NULL与IS NOT NULL、投影列名/alias及sqlite Row索引/keys、默认BINARY排序、多列/DESC/LIMIT、UNION去重、LEFT JOIN缺右行/重复列、count返回一行/空集合语义。必须依据已核精确DDL保证唯一性，不能用dict索引静默覆盖损坏重复。非目标行若为筛选/排序/cache而实际读取也付read/probe；唯一证据费仍仅完整唯一实际行，不能把cache消费免成零工作。
5. **缓存持有与重复收费**：记录缓存、原行、投影、正文、Python canonical及parse衍生物的持有时段；seen免重复evidence不免实际重复decode/扫描/投影。若真实旧validator反复消费同一付费cache，应给每次消费的明确read-work，不能只第一次SQL账。schema完整列typed证据和完整引用闭包不删字段。
6. **编码和异常**：UTF8/UTF16LE/BE含ASCII/汉字/补充字符/控制字符/NUL/非法TEXT、SQLNULL/int64边界都核原口径；octet_length物理字节仅用于预留而非持久证据。错误发生在prepare/execute/fetch/lookahead/迭代/原包装时仍保有限存储分类，真正取消保首因；未知SQL拒绝，caller活动事务不动。
7. **硬界不动**：READ/PROBE各536870912、query65536（含封存BEGIN/ROLLBACK2槽）、原ReadLimits和52/profile1不改。metadata/count/pager/header常数与真实次数加入同一本账，不能新增无限免费control、S1 jsonb/upper政策、serialize/dbstat或新连接。cleanup不被业务额度耗尽挡住，失败必须报告真实in_transaction。
8. **非空正常与独立反例**：保作者focused-04九正常首次超512MiB原件，再核新fixed真实正常九编码材料、原所有关系与129旧验收；低预算验证首次扫描/复制未发生，六维±1、重复、enumeration和cleanup。作者成功只作来源证据，正式调度后由本审在本树独立环境运行必要小反例；不无变化重复fullcheck、不把全拒误当修复成功。

固定元数据与一次只读事务缓存可成为减少重复扫描的实现手段，但本准备不认证正在合并的方案；是否满足上述顺序、真实重复工作和旧SQL语义，须对新fixed逐行审并独立实际探针。现仍保留原启动全库校验/ChangePreview既有前置分配风险，C2修复不关闭正式physical dispatch/current scope/permission、公开frame/page/canonical、父FR、指定双外审、目标OS、CI/远端等门。

## 5. 当前结论与后续触发

准备完成；**修复通过状态：待新fixed及正式复审，不是Pass**。仅接收旧固定事实和重新打开的缺口；不采用WIP，不借S1未批算法。下一输入应是精确新两writer/54清单、SQL/EXPLAIN及sourceID约束、真实费用账和正常/拒绝/±1/cleanup原日志。收到root正式followup后才进入运行反例与修后结论；当前结束准备阶段释放槽。

## 6. 首次正式受审候选2c425及实际不通过记录

root正式调度后实读固定产品 `2c4257b1df2c2e1c6d636d3c4ce7ecc4755071c1`，parent为旧过程5b118759；diff-tree恰原两writer。模块59749B/SHA `e174bcee70661db53b387145870f615dfd0a1549e59787ce64a63af68dd1f409`、专测64589B/SHA `90b9c54921fe125fe59fc2ae4fc274508509823df49b7c6cac9a8bfad1654406` 均实际current=该Git blob。新manifest12542B/SHA `c3e2b97b5592216b86ed5730a0dd2aa0365076fe1066bc37b8e071063ad1991d`（当时过程未提交，不冒称属于产品commit），固定54/54与其核同，52/52再等423b原字节。原51个模板set与256完全同，排序JSON摘要均 `5ba1b3f893c7a7147187d69e7cfb08f58d7b45663cf7340b1440b90c8cc92db5`。

已全文读新模块（89bab4/20f821/5a6c0f）；新测试按已全文读旧129源加固定完整diff dc6b23复核，包含12新增case，共141。身份85768e、固定清单/51模板ccf4db均静态exit0。新reader路径使用同snapshot缓存、原完整sqlite.Row、先最高列native metadata、实际sourceID gate、流式numeric rowid枚举及fetch lookahead预付，未改caps或原52。上述结构不等于前门全面成立；本轮发现以下实际反例。

### P2-PR-01：最终完整行SELECT仍全表扫描，固定单行票不足

位置：2c425模块 `_cost` 的完整行物化调用（本次源码约635行）调用 `_bounded_select("SELECT * FROM ... WHERE rowid=?")`。该重写把rowid条件包进CASE的THEN，导致SQLite无法使用SeekRowid。调用只按目标完整行和单行header/22页付费，实际会先对每个非目标行计算highest列typeof；本页TEXT路径即便P5=128仍执行OP_Column memcpy，证据费/表native scan票没有覆盖这次额外全表过程。

独立本树 `.venv/bin/python`，真实JobStore3→原create_project/put_blob 300条小非空材料，每条payload约1KiB，随后直接调用实际 `_MeteredGate._cost("job_blobs",末行rowid)`。这是低层门的机制审查，不冒称300条Job材料全部经过公开resolution。probe开始打印实际模块59749/e174，原audit观察实际3.50.4/sourceID与受支持值完全相同；没有使用另一树环境或改产品代码。

实际SQL为：

```sql
SELECT * FROM "job_blobs" NOT INDEXED
WHERE CASE WHEN typeof("payload") IN ('text','integer','null')
THEN (rowid=?) ELSE 0 END
```

SQLite真实EXPLAIN：cursor0有Rewind、Next和payload Column(P5=128)，没有SeekRowid；完整行payload Column另P5=0。目标是最后一行，首step已沿所有前置行执行上述typeof。独立只读SQLite oracle（不import当时作者已开始修改的新WIP）从同一已关闭fixture原件核到：300行payload字节和306490、每条1020–1022B，dbstat最大record1128<4096-35=4061，全部本页。这里只用dbstat证明自有fixture的local分支，不把它引入产品或采用为新算法。根据已固定SQLite本页memcpy切点，仅这300次payload复制下界306490B就超过该次SQL整票263503（其中control262211）；尚未计其它列、步进和控制。故不是仅凭normal费用接近上限推断失败，也不是把VM step数量等同bytes。

实际原件目录 `/tmp/t01-c2-independent-preprobe-20261022-01/`，均未覆盖旧临时文件；首run已封存manifest后才新增oracle，未复跑改写首run。

| 原件 | bytes | SHA256 |
| --- | ---: | --- |
| scan_probe.py | 2045 | 3155cb37c4ba7b5f236ed81035f28319d6f5e5690ec415a6ad927e4a56b6ce36 |
| scan-run-01.log | 770 | 6568ae908f5eafc5d2ff634bc4bedd98708db339b9af5313a00259753592771f |
| scan-evidence.json（SQL/票/完整EXPLAIN） | 4309 | ef0c5b3c456e05f27f8fe58c30f735bf4434170a40346fa130a81211c9b8d3c4 |
| scan-ledger.json | 1241394 | 3f5d51a2a5383b03691e2d8ebf8c4a80573fb1ebe6d171f454464f01cba52fe4 |
| run-01-sealed-manifest.json | 778 | e4f4f35fd6a196391dd672b7baed0dc899b48773c25ccc2df54468269fd21611 |
| copy_bound_probe.py | 1048 | b4617349828594d45850e937c97d2ab0374c9ec246ed04aa5293e5fcb027a8cd |
| copy-bound-run-01.log | 250 | 8b461374a1c8f72b6d7f19fa0d3e0478d71dba4b266e5cdbf9ea9c8fc500fb51 |
| copy-lower-bound.json | 272 | cee002fc1dfe184a90746d93c25000f65fd7cb8aad9cedfc566fb2c9c206e28b |
| scan.sqlite（自有原writer材料） | 802816 | 8d1c5e1797331e30d06c7ac4851fab2000499f36092222243b6e059492ea805b |

首执行f3969e真实exit0、fa6d5b读回；oracle436f53真实exit0、ec1b8e读回；hash读取48627d。命令exit0表明反例采集成功，不等于产品通过。已即时通知root及作者。建议使真实rowid等值谓词处于可SeekRowid的外层，同时保持最高列先读的独立副谓词，并把所有最终SELECT*纳入EXPLAIN矩阵。原新测试的plan过滤只选native/point-set/LEFT JOIN，没有收本次最终SELECT*；所以141通过没有排除此路径。

本次2c425结论：**不通过资源前门独审，P2-PR-01待新候选修复**。作者随后已接受并准备在原两writer修复；本报告保留首失败，不将未来处置提前改成关闭。

### 同期作者自查事项（尚非本审独立实证）

root和作者另外通知：新增真实列名rowid/_rowid_/oid可遮蔽numeric枚举，_columns当时只拒hidden和_t01_rowkey，返回后exact int检查晚于TEXT物化。作者正提交自己的真实反例并计划修复。此处准确记为作者来源的开放事项，不把作者工具549a43当本审执行、不先声明关闭。新fixed需同时核枚举前大小写不敏感别名拒绝、统一真实alias、空表和异常清理。

作者已开始上述两writer新修后，本审停止运行当前checkout产品，继续固定2c425及SQLite源码静态复核。后续新fixed身份/正常检查与独立复验另追加；原2c425的141/check等只能覆盖它自己的字节。

## 7. 最终修订身份与静态复核

本节追加于前述2c425不通过记录之后，原18377B前缀逐字保留。最终受审产品为 `ab792c494db09ada1f20d0a598c3e0c96c338992`，parent实现提交 `0223d70212ac21ea07f9d180a7efeacac6485b8f`，其parent为保留2c425及反例的过程 `aa199fb179a38681d78a5bb58fb76ef76023fe53`；最终作者过程为 `bef8e431a9a73edae6d482530e90c01eaa091ad4`，parent恰ab792。过程增量恰8个新作者文档/证据文件，未纳入尚由本审追加的报告，不把作者过程提交视为独审结论。

| 最终固定材料 | bytes | SHA256 |
| --- | ---: | --- |
| operation_evidence.py | 60251 | e47f2689dcbf9519aeb3f64026094545e41f5401f309520bc805eb85f3fb56c8 |
| test_project_operation_evidence.py | 70063 | 8b03aeac29e0a6ca1f53c8b3a81aef31b6110d8f722a4b275e6a7a10ed77cd6f |
| preprobe-repair-review-input-r2.json | 6848 | eb5fb7f1cf0fe8608a941e4680e55c43c3f9cfd03f11002d6955c0cd10e65aa7 |
| preprobe-repair-candidate-manifest-r2.json | 12387 | 02e6962ae0174674b16b432f975b90e861803fcbe355ee132f34ddd82f6be337 |
| preprobe-repair-checks-r2.json | 3165 | ba789eb4171d201bb71562f073e422b005e80d5100565ea0355d51a094f4ee1f |
| preprobe-repair-source-proof-r2.json | 1613 | 4e0d436c5551b8a14752e10c9b2e58644c60b0213fa9853855c90557803b8849 |
| preprobe-resource-repair-r2.md | 3509 | e236253ba3446b6746ace523f229585438c58f42b452579febf3b086d47b199e |
| preprobe-repair-evidence-r2.json | 184680 | 3f3b2f271412dc22b8dbfbae30150922a4b96f09481abb855ef626859f8a71e1 |
| preprobe-repair-evidence-r2.zip | 21731943 | 7518d343440bf904b160c97621dfec5c1d27c7a8f9ebf3c99150edeb99a0a6f2 |

新两writer实际current=ab792 Git，完整54再逐current/ab792/manifest长度与SHA核同，52readonly再等423b原Git字节（0c94eb）；作者7输入及2writer逐当前/bef8 Git核同，过程8文件集合精确（a1c6be）。外置final-git-receipt.json为3478B/`68363650bd881c42231e21d8ebd4972e5fb1430daa34800a9245c3e454c0eced`，属于提交后的外置绑定，未冒称已包含在此前ZIP。原19044独审、原430条ZIP13284166B/d09dde1e及270143B/b8b49cac原index实际current=5b Git，均未修改。

已实读2c425→ab792完整两writer差异（1a1031），结合前述已全文读取的源码完成新交互复核；身份27da92。主要修订仅为：非sqlite_master枚举前调用完整有界_columns；大小写不敏感拒rowid/_rowid_/oid/_t01_rowkey及hidden/generated；内部统一未遮蔽_rowid_；最终完整行等值谓词独立于CASE；关闭游标捕获BaseException并保first身份。原51 SQL模板和同连接旧validator绑定未扩大，新控制票与原各cap未提高。

现路径在metadata读取前支付statement、物理header及local/page票；native实际计划最高列先读、P5仅128/192，从实际物理字节上界预留probe后才执行length/NUL/转码/费用SQL；精确完整typed证据费通过后才读取完整行。全库原aggregate由已付的完整metadata/schema cache提供，原WHERE/ORDER/JOIN/UNION仍用已界rowid point-set实际SQLite语义，重复返回及遍历继续read计费，不拿seen抹除工作。schema cache仍核实际原catalog，并非另一套简化接受标准。原数据类型/NULL与数据库编码的原raw guard口径、唯一(table,rowid) canonical UTF8证据费口径保持分离。

已补读SQLite BTCURSOR_MAX_DEPTH20、moveToRoot/moveToChild/First/Next源码：普通First/Next的40页票有20层/非空child与异常退出依据，严格递增numeric rowid拒重复/坏DAG。最终不依靠count结果倒扣首次完整count；普通SQL筛选使用先界点集而不是原无界count/WHERE扫描。实际完整路径EXPLAIN文件26718396B/`cd98e9844b80d47b6864a9338570cb4b876012be287c8137baf0d462914a7a0d`，独立解析全部1243计划：40纯numeric枚举均无Column；其余真实OpenRead游标均有SeekRowid且无Rewind/Next，无Count/OpenAutoindex；含152 native和191最终完整行计划。该记录是实际atomic材料经过的路径集合，不冒称逐一动态穷尽所有51模板/所有损坏库；其它模板分支由固定源码和原160专项覆盖补充。

## 8. 独立修后实际复验

仅使用本树 `.venv/bin/python`（CPython3.12.12、SQLite3.50.4），唯一新目录 `/tmp/t01-c2-independent-preprobe-r2-20261022-01/`。无全仓重跑，无新增损坏文件或大字段；别名检查使用小型正常SQL表/DDL，close使用受控spy。作者全套与本审小探针分开；spy是控制机制验证，不冒称OS真实内存耗尽/磁盘故障或异步信号实测。

**P2-PR-01定点关闭**：原300行脚本逐字复制为同hash3155cb37，使用独立新fixture/日志，不覆盖首反例。f14c85实际exit0，a4dfb6读回，4d3904另断言并封存。source开始为60251/e47；实际最终SQL为 `WHERE _rowid_=? AND CASE WHEN typeof("payload") ... THEN (1) ELSE 0 END`，真实OpenRead游标有SeekRowid、无Rewind/Next，最高payload Column先P5=128，目标完整行真实费用核同。单SQL票263759；现在仅寻址目标行，不再把300行payload复制隐藏在单行票下。原2c425的306490>263503反例继续有效，不能倒称原版通过。

另执行独立matrix_probe.py一次（ec48e6真实exit0），共42个有断言的读取；开始及结束模块SHA均e47，所有数据前后dump相同、本次事务均不再活动：

| 独立范围 | 数量 | 实际结果 |
| --- | ---: | --- |
| UTF8/UTF16LE/UTF16BE真实原JobStore writer普通Job阳性 | 3 | job-record与原get_job DTO核同；同一BEGIN/ROLLBACK；每唯一实际完整typed行由独立json.dumps oracle逐一核金额 |
| evidence/selector/return/probe/read/query六维各-1/0/+1 | 18 | -1为resource-limit，0/+1与基准结果完全相同；probe使用真实peak而非settled低值 |
| evidence=1、probe=1、read=1、query=2低预算 | 4 | 均resource-limit；低probe不执行instr/replace/递归；低evidence不读取完整行；低read/query trace仅BEGIN/ROLLBACK |
| rowid/_rowid_/oid/_t01_rowkey各原样及大写的小表 | 8 | 有限incomplete，目标job_blobs未枚举行号、未native读取；schema自身先收费读取允许 |
| first无/resource/cancel × close MemoryError/KeyboardInterrupt/SQLite IOError | 9 | 有first时同一原对象且cleanup_failed=true；无first保原MemoryError/KeyboardInterrupt，SQLite经真实_Cursor.close边界转storage-failure；均关闭真实私有cursor并执行本次ROLLBACK |

因此作者来源的别名问题在本新固定版本获得独立小型复验关闭；新增close首因处理也有独立矩阵。未复造作者的1MiB alias或损坏overflow/empty-child文件。

三编码阳性独立总账如下，数字仅针对这些真实小材料：

| 编码 | evidence | queries含2控制 | readWork | probePeak |
| --- | ---: | ---: | ---: | ---: |
| UTF8 | 34564 | 2618 | 420290031 | 4717536 |
| UTF16LE | 34564 | 2618 | 403288079 | 161643600 |
| UTF16BE | 34564 | 2618 | 403288079 | 161643600 |

运行结束立即封存matrix manifest，不反复复跑凑正例。独立原件摘要：

| 相对上述目录的原件 | bytes | SHA256 |
| --- | ---: | --- |
| scan-run-01.log | 743 | 3da738fc22d0a620d20a0ac46982b5b42f870041419dce58fd96b15240580ceb |
| scan/scan-evidence.json | 3929 | d75075eab47e0c3c690212d344512315659cef9613718cefdb3118d3189330fe |
| scan/scan-ledger.json | 1243834 | c2d701ba176d692621c99d788282b4afd4249a1661c2e437e41b4d822da64881 |
| scan-run-01-sealed-manifest.json | 798 | 227fee5e245a9bb712e27a39ad70f2d26cdac77418442461639953aab7f87c24 |
| matrix_probe.py | 10442 | 51e155fe8bf5800900d6880878f881d3e26635067b180bb0ccb7ae5455aab5f1 |
| matrix-run-01.log | 298 | ddf45d96b9ca24fa6346569ddf5141c63776c9d64fb146053c3477ab8ccce15c |
| matrix-results.json | 6219 | d99a24f96d958c1776e4e0ed977f96a07434625e6afc931f9b82041d0816d7d2 |
| matrix-run-01-sealed-manifest.json（76文件，含自有DB） | 10684 | 7ac78da6280835d83e40b5e13397671d5366e2bc2fdb2fece7b6209ff826a874 |
| independent-review-evidence-r2.zip（58文件，排除运行DB） | 2660743 | d133e74caf72c2ef60cbd05406413de1c1aa1109650816216c5f4b70e9109f40 |
| independent-review-evidence-r2.json | 15057 | a8f2d3dedd280c5a870da55ffcbeb9c1ecf2f093dcfbf2ea54444b434bdd00f0 |

独立ZIP另保留归档核读脚本/首读取错误/修正结果及作者账的静态核算，不冒称属于作者此前已冻结的ZIP。

## 9. 作者同版正常检查、首失败与原始绑定

已全文读r2-check-03.log8994B/SHA `0bb8e7df0e0171e334dc461a429422770b0f4007c18d4599e5f7ff23295173c6`，实际pipeline覆盖lint/格式/类型、1125TS、build、ruff及3129Py/44既有skip，含160专项。已读source03原111B/1439dca3…日志核12件源。它们由作者实际运行，本审没有重跑全仓或source。

不是只根据日志末行推断exit：R2原ZIP内真实工具调用与返回逐当前原流核同，normal开始192d79/session74678至14c887 exit0；source de486a独立exit0。normal终态原sourceLine2789/call_8f56aa1e285b4333948f49b5dd0d67ec；source终态原sourceLine2742/call_5cfdd6c9f2484c0a8128f41c3975c14e。记录含Promise包装的真实nested result，未用外层成功替代独立子命令退出。

0223首正常失败日志11472B/`4489529fd98f10d00f776e48c5edadb7f24900747c874bf6c0f84fe26869b543`已读，ef5d16真实exit1保留，3128pass/1fail/44skip。ab792相对0223的完整diff只有原empty-child断言由“全库无native-metadata”收窄到“目标job_blobs无native-metadata”。本审静态读修前/后两份实际canary账：两者字节同，1283559B/`95e5a5ab83b84acde32e5fb7317ba897e069e7f31158b85e82d51f1f035093c6`，均125条sqlite_master native、目标job_blobs native0/完整body0。枚举前的新增schema验证本就需要已收费schema metadata，故此作用域修正有效；storage-failure断言和真实目标正文前拒绝、finally恢复均保留，没有把产品错误删断言交绿。

160份作者最终专项账本含170个gate run；本审逐正常summary重新核query连续编号/费用累计、唯一完整行证据费、probe hold/settle/scan累计及peak、逐query read公式，结果c73e9c静态exit0：141个正常ROLLBACK summary，max正常read524308902、max probePeak204940688。其余直接gate/取消/cleanup故障不能统称已释放。统计在作者原工作量定义内递推核同，不等同测得CPU/RSS或运行时间上界。

## 10. 最终归档核验与证据边界

R2 ZIP381成员集合唯一、安全相对名、无symlink，逐读到EOF的CRC及bytes/SHA、380个当下live artifact源字节全部独立核同；第381个为原tool JSONL，60条逐原source line/byte offset/response-item ordinal/tool ordinal/time/原bytes/callId核同，组成30完整pair。R2选择范围2519–2811，真正首tool record为2524，二者准确区分。与此前02的57pair/114条合计87pair/174条，修前记录仍属于修前字节。封存/check/commit后续不倒装进此前capture边界。

归档原流固定来源：`/Users/kyle/.codex/sessions/2026/10/21/rollout-2026-10-21T20-28-12-01a15e6e-f47e-7960-8e8b-d79eff4f21b8.jsonl`。本审首次读取器只解析一层JSON，遗漏de486a的Promise嵌套而触发KeyError（bd2516 exit1）；已先封存首脚本/错误原件，再修为递归读取，2e1b5a实际exit0，原件381项及三个关键真实退出全部核同。该错误属于本审归档读取脚本，不是产品或归档缺失，未隐藏或改写首失败。

作者既有focused01的11份中间失败账轮转缺失仍明确列在index；原日志和tool exit保留，没有重建，不能称全部中间账无缺。原focused04、首低预算反例、2c425别名与本审300行首反例、0223首正常失败均保留，不受此缺失影响。原C2旧430条/215pair与129专项归档、原19044独审保持原字节。

## 11. 最终独审意见

**最终产品ab792/作者过程bef8在本轮内部C2资源前门修复范围内，未发现未解阻断，支持交root重新收件。**P2-PR-01已由真实原反例定点关闭；大小写别名及close首因也经本审小型实际矩阵复验。这个结论只绑定上述最终两writer、完整54/52输入和同版来源；旧256/5b、2c425的历史正常/不通过状态保留，不将新结果追溯替换旧记录。

仍只支持明确3.50.4/sourceID及当前profile1，未知版本有限拒绝；官方同版本源码及真实EXPLAIN不等于各平台binary可复现证明。预算是工程工作/编码上界政策，不是全库CPU/RSS、容量、耗时或所有合法大Job都能读取的承诺。旧启动Store/Job全库校验与ChangePreview前置分配风险、首次IO/owner生命周期、物理dispatch/current read scope/permission、profile2与组合56、formal resolution、指定同版双外审、CI/远端/目标OS/真人及父FR门未由本审关闭。无GUI/native/网络/外发/模型/付费/打包、stage/commit/push/merge。审查者唯一仓库写入仍本文，原19044和作者材料不改。
