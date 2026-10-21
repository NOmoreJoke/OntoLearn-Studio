# C1 完整写前预算模型：独立审查

当前结论：预算模型可行；对下列实际 read-ready 源码与测试进行独立静态复核后，未发现预算方面的未解决实质问题。首次 INSERT 前的同连接只读计价覆盖真实新增10行、全库 rows/bytes/work、完整 catalog/snapshot、全部合法页与 editor 最坏编码，无需试写回滚、第二连接或修改 reader。此结论仅关闭本文列明身份的预算静态审查；最终五路径身份已在第7、8节核对，实际最终检查原件见第8节；事务/兼容由另一独立审查负责，不据此宣布正式创建服务或父Goal整体通过。主线独占五条产品/测试路径；本审仅写本报告。

## 范围与实际读取

新树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-create-core`，初始 adoption `ba2c6c293f9fd9e1742c9ab352dae5e3c951f6a4`，批准父基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。50项接收及47项只读保护由另一独立审查任务负责，本报告不重复其全清单审查。

本审实际读取了：

| 输入                          | bytes | SHA256                                                           |
| ----------------------------- | ----: | ---------------------------------------------------------------- |
| 最新 C1 授权                  |  8323 | 93528eb38395856af86a76edf9c26822ef406f8a32315282086a509db235d8b5 |
| 本树 AGENTS                   | 15852 | 78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759 |
| developer-common-instructions | 17891 | e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0 |
| 根合同独立复核                | 18372 | 517b29bf74765bdca633b2bbc128cd036b7517aae8a7cb47edf900ae3e2e3bad |
| 固定379916合同                | 39602 | ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3 |

工具 `7ba556` 首次规则批读中 common 中段被输出包装截断，已以 `167b8e` 另读精确全文并实际核 bytes/SHA；未把截断输出当全文。根复核及既有 seed/checkpoint/state/snapshot 源实际读取为 `36fe69`，ReadLimits/reader 全文为 `1e48ae`，固定合同分段读取为 `08ba99`、`3663dd`。未 import 或执行产品、测试、SQLite、构建、GUI、原生接口或网络；未借其他工作树环境，未创建 Goal 或改变父状态。

## 1. 必须先固定的模型事实

在同一个外层 BEGIN IMMEDIATE 中，只读核已打开的真实 JobStore3 结构、原全库 claim/占用、旧状态和其有限读取预算；幂等原 claim 先于 UUID 分配及新预算模型。新建场景才由 engine 分配新 UUID，再由原 request、原名称、已核逻辑 libraryEvidenceRef 与受控 origin 推导全部候选值。

此阶段的 origin/permission 只是业务材料，不证明真实权限、原 dispatch 物理库或真人。预算模型也不接路径或 mint scope/binding。

空白领域 snapshot 的确定 payload 是 project/new UUID、projectRevision0、dependencyVector空字典，state 为 mappingState空字典/definitions空数组/facts空数组。其 domain hash 含 project，不能拿别项目空 snapshot 的 hash 代用。genesis app 保留 name null、metadataVersion0、sequence0；最终 app 为请求原名称、metadataVersion1、sequence1，其他 draft/learning/audit 仍空。两 checkpoint 的 historyCoverage 都是 legacyDomainOperations0、legacyDomainRevision0、legacyHistory complete、applicationHistory from-format3。

纯模型先计算与现 canonical 完全相同的字符串和各自 hash；它们只用于首次写前计费。实际写入仍必须从真正存在的 genesis 生成 plan/context/receipt，并逐值核与预算候选一致；不相同全组回滚，不能把预测值当持久证明。

## 2. 新增持久行与全库费用

在所有新主键/hash 均无冲突且新 UUID 未占用时，最终净新增10行，分布为：

| 表               | 新行 | 计费内容                                                                |
| ---------------- | ---: | ----------------------------------------------------------------------- |
| projects         |    1 | 新UUID、revision0                                                       |
| snapshots        |    1 | domain hash、完整 canonical domain payload                              |
| app_projects     |    1 | 新UUID、metadataVersion1、sequence1、完整metadata、最终checkpoint hash  |
| app_checkpoints  |    2 | genesis及最终checkpoint的 id/project/domain_snapshot/完整payload        |
| app_origins      |    1 | 新UUID、真实genesis ref、domain_revision0、legacy_operations0、created  |
| public_projects  |    1 | 公开/内部均为同新UUID                                                   |
| operation_claims |    1 | operation/project/job NULL/fingerprint/kind application/完整context     |
| app_operations   |    1 | project/sequence1/operation/kind application/plan_hash/domain_revision0 |
| app_receipts     |    1 | project/operation/完整receipt payload                                   |

空白创建不增加 versions、definitions、facts、commits、Job 或其他账本。app_projects 的中间 metadata0/seq0/NULL head 是同一行的未提交过程，不重复计为第二持久行。候选 snapshot/checkpoint id 已存在或新id互撞时必须走冲突拒绝，不用 INSERT OR IGNORE 使实际增量与模型悄悄不同。

reader 的费用不是 SQLite 物理文件大小：每表每列 `coalesce(length(CAST(column AS BLOB)),0)` 的总和才是实际口径。NULL计0，整数按SQLite的CAST结果计，JSON先依现 canonical 序列化为字符串，再把该字符串整体计一次。

为避免暗中假定 SQLite database encoding，候选 typed scalar 最稳的精确估价是在同一现有连接只读执行 `SELECT coalesce(length(CAST(? AS BLOB)),0)`。本新增记录的实际列值只有严格 str/int/None；应确保绑定类型与实际持久列类型一致。这是只读表达式计价，不是创建库或试写。若只用 Python UTF-8 长度，须先证明适用的真实数据库编码/列类型前提，不能把名字合法UTF-8直接当 CAST 一定UTF-8。

令当前 reader 同口径 aggregate 为 R/B，app_operations行数O，snapshots行数S，新候选净费用D，则新增后必须满足：

```text
projectCount + 1 <= limits.projects
R + 10 <= limits.validation_rows
B + D <= limits.validation_bytes
(B + D) * (1 + (O + 1) + (S + 1)) <= limits.validation_work
```

这里按10行核的前提是上表所有 id 均确实新增；schema对象数/总SQL字节、表数/列数没有DDL增量，仍须原有限结构校验。不能只用当前 `B*(1+O+S)` 或只乘新项目自己的O/S。

静态 canonical 工具 `8420de` 独立建模了规范UUID、名称“新项目”的例子：新增10行在UTF-8数据库前提下合计4561B，其中 projects37、snapshots212、app_projects193、app_checkpoints1635、app_origins109、public_projects72、operation_claims1294、app_operations149、app_receipts860；context+plan合计1642B。它是明确 fixture 的对照数值，不是任意名称/库编码的固定费用，不可直接作为生产常量。

## 3. 完整目录、快照和每一种真实页

现有所有目录行与新行都须按同实际政策验证完整metadata、内部身份和完整行编码；不能只核新项目。尤其 new internal UUID 是36个ASCII字节，若 ReadLimits.identity_bytes 被合法收紧到小于36，reader._validate会拒绝新内部ID，创建必须在首次写前拒绝，不能只把 identity_bytes 用于 editor。

新目录按公开UUID BINARY顺序插入候选，再冻结其完整行编码长度。快照必须匹配 reader 实际 guard：

```text
sum(encodedRowBytes) + 2 + count <= limits.snapshot_bytes
768 + count * (limits.catalog_row_bytes + 64) <= limits.retained_bytes
```

reader 现实现的快照计费比真实 canonical 数组多一个字节；不能在±1用例中改用 `len(canonical(items))`。本静态四行 fixture 的数组实际2071B，reader guard为2072B；以2071为限会在 reader 拒绝。

所有 page_size 从1到实际 page_items 均应枚举真实可达 offset（0、size、2size……），按该组完整 items 计算整页。snapshotId 是36个ASCII字符；非末页 nextCursor 是93个ASCII字符，末页是 JSON null；total/offset/字段名/标点/转义也须计费。可以使用已证明覆盖这些页的上界，但不能假定 reader 按 byte预算自动缩小固定行数。

实际静态反例 `8420de`：4条目录行的编码长度是292、292、292、1190B，最后一条是900个ASCII z的名称，page_items收紧为3。size3两页分别1091/1312B、size1各页最大1312B，全部能放入1400B；但size2末页是1605B，不能放入1400B。只检查最大页大小或只检查一行页都会漏掉这一拒绝边界。

单目录 reserve 能放入空闲 reader，不代表任意已有快照占用状态也一定能读；snapshots/TTL/剩余留存是原有限运行资源语义，不需要创建事务替未来所有 reader 的占用预订槽位。

## 4. metadata 与所有合法 editor 的工作区

必须核完整 canonical metadata，不能把名称本身≤4096当充分条件。独立算式 `8420de`：4096个ASCII x得到metadata4178B；4014个ASCII x恰4096B；4014个引号字符得到8110B。名称不截断、不 trim/NFC/casefold，转义扩张必须由完整编码计算。

初始 workspace 还含 inputSnapshotId、workspaceVersion 和 `{editor,state:missing}`。reader 对 editor 只核非空/有效UTF-8/identity字节界，并不禁一般控制字符。若 editor UTF-8 界为m，`U+0001`重复m次是合法且可达到的最坏 JSON 编码：每一个输入字节变成6个ASCII字节。因此可用这个实际字符串计算完整 workspace 上界，不必另复制 editor 政策或只测m个ASCII。

静态 fixture 名称 small、editor 512个ASCII时完整workspace953B，改成512个U+0001时3513B，差2560B。workspace_bytes若收紧为1000，前者通过而后者拒绝。首次写前相容模型必须按后者拒绝，不可在创建成功后才发现合法editor无法读。

## 5. 实现审查依据

- 先界形状/字符串，再构造深层候选；ReadLimits只读消费实际类型/字段，不能复制可漂移常量或放宽 reader。
- 旧库聚合与新候选的定价都在同一唯一writer事务、首INSERT之前；不以写后计费/rollback试写代替。
- 上表完整行集合/类型/值与写后实际逐项相同；不漏残留辅助行、重复snapshot、真实hash碰撞或新字段。
- 完整目录所有size/可达offset、快照guard多1字节、36字节新UUID、editor最坏编码和真实全库work因子分别测试±1。
- 此前静态算式不代替真实SQLite/authorizer/首写拒绝/完整dump/真实退出证据，也不关闭创建、resolution、宿主、物理位置或父FR门。

以下将上述算式与实际 read-ready 实现及测试逐项对应；不重复另一审查人的采纳/完整事务工作。

## 6. 实际 read-ready 预算定点复核

首次 read-ready 全文读取及身份核验为工具 `b21c71`、`e5985e`：module 20246B / `a998ecabd3942e0f271545c105fa1216e66c49ea71d9079523a817241979c3c5`，test 25875B / `78de84517c909fde218821378f424bc1ef515cb296d32ac00a602b9ece675df1`。写报告前再次核验发现主线已补 UUID 标量先界长；已报告该漂移并以 `fc25b5`、`a1e5a4`、`6fa8f1`、`2b2f23`、`23351a` 重新读取当前两文件全部内容。当前预算审查对象如下：

| 实际文件                                                          | bytes | SHA256                                                           |
| ----------------------------------------------------------------- | ----: | ---------------------------------------------------------------- |
| packages/engine/src/ontolearn_engine/project/project_lifecycle.py | 20345 | f748d8cc6aa892da0231e1cbd830a9b8ee48a70f875a442b54ae32ff7223ca32 |
| packages/engine/tests/test_project_create_contract.py             | 26464 | 5a89e7ae76f985ff8c69b02accd9af755d9a52489f47462a7a3cf7e23064c18d |
| docs/iterations/T01/project-create-core-C1.md                     | 10394 | 635d9fdd4ac8f334b5e9a3c38a657a9f4098058da9739e0e5f02d3524077b37b |

实现文档全文与原目标日志的实际读取、核 hash 为工具 `375b19`；文档身份还由 `a79e2a` 复核。此处列表是本次已审读对象，不替代主线最终五路径清单。

### 6.1 真实实现与算式一致

`request_value` / `origin_value` 在深层复制或解析前界定固定字典形状、精确版本类型、固定36字符 UUID、名称字符/UTF-8 界和 canonical 总界。补充的 UUID `len==36` 在 `uuid_ref` 调用前短路，不改变候选值或预算结果。`ReadLimits` 直接消费 frozen reader 的真实对象，不新增 reader 配置或复制放宽限额。

`model` 构造第2节全部10条候选行，保留所有 genesis、public mapping、app context/plan、receipt、head 与完整 metadata。`preflight` 先复用原 reader `_preflight`；`_totals` 以真实表和列计算当前全部 rows/CAST BLOB bytes，`_row_size` 在同一已打开 writer 连接对实际 str/int/None 参数只读 CAST。增量按候选每条真实列值相加，work 使用新增后的全库 app_operations/snapshots 行数。首次 INSERT 位于 `preflight` 返回及 `create_preflight` hook 后；没有第二连接、临时表、试写或 rollback 计费。

全目录旧行使用 reader `_row` 和当前收紧政策，另核全部内部ID；新UUID明确按 identity_bytes 检查。追加新完整行后按公开UUID排序，逐行 metadata/rowbytes、快照 `sum+2+count` 和 reserve `768+count*(catalog_row_bytes+64)` 与第3节对应。嵌套循环覆盖 size=1..page_items 的每个真实 offset，整页包含36字符 snapshotId、93字符非末 cursor、末页 null、total/offset。固定占位值的编码长度与实际 UUID/cursor 相同。初始 workspace 包含完整新行及 inputSnapshotId，并使用合法 `U+0001 * identity_bytes` 覆盖可达6倍 editor 转义。

预测 hash 仅构造待计费材料。真实 seed 完成后读取 `project_checkpoint`，与模型 genesis 核同，再以 `actual_genesis` 重构实际 plan/context/receipt；写后逐表逐行值核同且全库 counts/bytes 与 projected 完全相等。这一复核不把预算预测提升为已持久事实。

无需为没有新增 DDL 的 schema_bytes 另造新计费公式：现有 exact reader `_preflight` 已在首次写前调用；本次新增路径没有改变 schema 对象/SQL。运行中其他 reader 已占槽位不属于本次创建应保证的全部未来资源，本模型仍只要求一个完整新目录可按 frozen reserve 容纳。未将这两点误记为新增预算遗漏。

### 6.2 现有测试确实针对独立边界

本审只读取测试源码，没有执行测试。与预算有关的现有覆盖包括：

- 新增10行与真实行值/真实 SQL 总费用对照；真实 reader 读取完整 catalog 及控制字符 editor workspace。
- 10类首写前资源不足分别由 SQLite authorizer 记录 INSERT 尝试，并对照完整 logical dump，包含 identity35、metadata/catalog/snapshot/page/workspace、全库 rows/bytes/work、retained。
- 11个预算字段分别 -1/0/+1：metadata_bytes、catalog_row_bytes、snapshot_bytes、page_bytes、workspace_bytes、validation_rows、validation_bytes、validation_work、retained_bytes、identity_bytes、projects。阈值来自独立真实已提交参考 DB 的全表 SQL aggregate、真实 reader 全部1..64页及最坏 editor workspace，随后另建目标 DB 测拒绝/接受；没有从本次 preflight 返回值反推期望。固定UUID、固定名称和同长迁移身份使对应 DB 的实际编码阈值可比较。
- metadata 4096 ASCII→4178B拒绝、4014 ASCII→4096B接受及引号扩张拒绝；workspace1000拒绝最坏editor；page_items3 fixture 明确证明最大size与所有单行页都可放入而size2不可放入，要求首次写前拒绝。
- 新增大标量用例把 operationId/hostClientId/engineSessionId 各置为1000000个字符，替换 UUID parser 断言其只接收36字符，并要求 zero_write 拒绝。该测试对应最新小改，未获得其运行结果前不记为已执行通过。

第一条实际原子用例使用实现 `_totals/_row_size` 作一致性核对，单凭它不能独立证明公式正确；上述11字段测试另对真实 SQL/reader 实测阈值，补足了这一证据区别。页反例测试构造新候选行以隔离页分组反例，本审也保留第3节不 import 产品的独立静态算式，未把二者混为独立运行验证。

### 6.3 已有运行记录、待补证据与结论边界

本审独立读取 `/tmp/t01-create-core-target-pytest-03.log`，180B / SHA256 `327bec4cf07548afcc371ff8c926303a49153b7403cd5f232a9b2f1abed1c1b4`，完整内容显示 `126 passed in 4.72s`。原运行工具 `28f39e` exit0由主线报告；本审未亲自执行该命令，也未把该旧目标记录归到新增 UUID 用例后的当前身份。主线另报 ruff06 exit0，但本审未核其完整原件，不据此填写本审已验证项。

预算静态结论：对本节明确 SHA 的源码及测试，无待解决预算实质问题；初始模型建议已得到具体实现和针对性边界测试。仍待主线提供最终五路径 bytes/SHA、漂移后的目标与完整检查原件；获得后仅作身份/已有证据对齐，不重复运行产品或数据库。采纳、完整事务/兼容、最终完整 check 由相应主线/独立审查负责。本文不关闭正式 create/resolution、真实权限/位置/dispatch binding、宿主或父FR门，不把提案、静态阅读或他人日志当本审亲跑的产品 Pass。

## 7. 最终候选五身份与 P2 修复定点复核

主线在先前候选后修复创建 claim 借用 domain receipt 的绑定问题。本审以工具 `0de9f8` 独立核验下列五文件 bytes/SHA 与主线候选通知 `2e0b92` 一致，并以 `a233c8`、`8ddf19` 定点重读全部预算模型/计费/执行路径、原预算边界测试、新回归测试及 Job3 receipt 核同调用。此轮只更新本报告，未执行产品、DB或测试。

| 最终候选输入                                                      | bytes | SHA256                                                           |
| ----------------------------------------------------------------- | ----: | ---------------------------------------------------------------- |
| packages/engine/src/ontolearn_engine/project/project_lifecycle.py | 20932 | a43365c1615082a0229de0d8e48569227fa930a7c3a7f869360975d72f30d104 |
| packages/engine/src/ontolearn_engine/storage.py                   | 76042 | fbef0d0ace0a01b9ced5eaecaf83aeb9306258c0cbfa5fd98a6d79e46bc5a39a |
| packages/engine/src/ontolearn_engine/job_store.py                 | 87227 | 8896c3e30007e1dec04eaf47ae5bb5c33a1e9b3a1d016cb9165f99d8b4deeacc |
| packages/engine/src/ontolearn_engine/project/format3.py           | 32169 | 505d0beb124534b2ab2e6c1716df53ef7b8108bedb57f5300fcb79a68e955782 |
| packages/engine/tests/test_project_create_contract.py             | 27843 | de02dcf022da0784e2d5d31dc0d29f8b2ca5cf0691cd2ca19835cd136c91020a |

修复在 `creation_context` 中直接读取 app_origins、app_operations、app_receipts 三种实际 immutable 行，并逐值比较模型预期；Job3 再比较完整 history 验证返回的真实 receipt。新增操作均为同连接只读核验，没有新增候选字段、表、持久行或写入阶段。`model` 的10行内容、`_totals/_row_size` 口径、`preflight` 全库 rows/bytes/work、全目录每种页/快照/reserve、最坏 editor workspace、实际 genesis 后重构和写后逐行/aggregate 核同均未发生预算算法漂移。

为后续身份对齐，stdlib AST 只解析源码并取函数原文（没有 import/执行产品），当前 model SHA `2f88183e5fd0210ef49b7f97a5b96b71b84d173165b51f664e4f3f27cdd45458`，preflight SHA `2e56afa2207f7e412187a93cd43d7be0b58921ccc7466fc6ded4436e73f557e5`；这些是本轮函数原文指纹，不冒充旧候选自动 diff 的执行记录。

新增 `test_creation_claim_cannot_borrow_a_valid_domain_receipt` 明确先创建真实 domain receipt，再植入自洽但没有实际创建效果的 claim，要求 creation_context、Job3验证、重新打开拒绝并保留 dump。该用例属于另一审查人的事务/兼容范围，本审只确认其不改变预算前提或替代既有预算边界测试。

本轮预算静态结论仍为无未解决实质问题。主线通报较早 target04 的 `59c735` exit0、127 passed in 4.68s；本审尚未核原件，且该记录不是本节最终候选的 target06/fullcheck，故不写为当前候选已运行通过。target06 和最终完整检查仍待实际结果与原件后再对齐。

## 8. 最终检查原件对齐与预算审查关闭

本节取代第6、7节历史阶段的“等待最终身份/检查”状态。本审仍只读取原件、核文件身份和更新唯一报告，没有重新运行产品、测试、数据库、构建或 verify:sources。

工具 `885391` 再次独立读取第7节五文件，bytes/SHA全部相同；没有发生产品或测试漂移。同工具全文读取最终实现文档，10867B / SHA256 `13bcacbd9e3031effe8827856215183a2def15ef2209df175b44a2985a8b6305`，其新增P2真实不可变行/receipt绑定说明与前次定点核对相符，没有改预算公式或放宽原政策。

工具 `97e034` 完整读取并独立核验最终 target06、fullcheck 日志；工具 `fbbdb5` 定位并全文读取 sourceverify 原件，三份身份如下：

| 已读取实际原件                             | bytes | SHA256                                                           | 原件显示结果                                                                                    |
| ------------------------------------------ | ----: | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| /tmp/t01-create-core-target-pytest-06.log  |   180 | f3e954e07c05a2ae600a53f52a9c1334a4579c5ec29cd01bdc435f1ad37d4298 | 128 passed in 4.81s                                                                             |
| /tmp/t01-create-core-check-01.log          |  8667 | 897bd1596e9f61a55baa2a07531208c9adce8a488f22644bbd723f474a1bc2a7 | lint/format/typecheck/build完成；22个TS测试文件、1125 tests通过；2969 Python passed、44 skipped |
| /tmp/t01-create-core-verify-sources-01.log |   111 | 1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536 | 已核对12个归档源文件                                                                            |

上述日志原文不含 shell exit 字段。实际终态 exit0由主线原工具提供：target06 启动 `b50a2c` / session98989 / terminal `53abda`；独立完整 check 命令 `79a7dd` / session96986 / terminal `3b62e4`；sourceverify 独立末命令 `7c9c20` exit0。本审将“亲自读取并核验日志原件”和“主线提供实际命令终态”分开登记，不伪称自己执行。完整 check 的 Python记录为收集3013项、2969通过与44跳过，跳过项不记为通过；本次目标128项包含最新候选回归，不再借较早126/127项记录证明当前候选。

主线另通报 `536151` 已对47 readonly与adoption50逐项核Git/current/SHA相同；该接收/保护清单属于另一独立审查范围，本审不以该通报替代自己未重复执行的全清单验证。verify:sources 的12个归档源也不等同47/50全清单。

最终预算结论：第7节最终五候选身份保持不变，完整写前预算模型及静态边界反例均已对应真实实现与针对性测试，最新实际目标/完整检查原件已对齐，无未解决预算实质问题，本预算独审关闭。此结论只证明本报告限定的内部C1预算实现与其证据一致，不认证真实权限、路径、scope/dispatch binding，不交付正式create/resolution或解除父FR、双外审、CI/合并等后续门。
