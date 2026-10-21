# I05 profile Job / artifact / selection 供方方案独立审查

首稿结论：**方案阶段暂不通过**。67555B/09d25b0c 的 r1 主稿有两项具体 P2：**PS-01，正常 N3 正例的 rows-json≤4096B 不可达到；PS-02，I05 私有 rows 与原公开 row 的形状不同，缺少明确的有限展示转换合同**。均已在形成报告前发送 root 和作者 create_core_review；本报告不替作者修改原稿，也不把源身份/静态算术核同当作真实 Job 链运行通过。

## 1. 审查身份、边界与固定原件

审查者 `/root/create_budget_review` 未参与此主稿编写。唯一新写路径为本报告。树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-create-core`，实际 HEAD `7753666d2cfda48c76ce59fa1ad6f34802c48eed`。没有改主稿、作者 supporting 原件、任何产品/测试或 AGENTS，没有 stage/commit、新产品树/环境、import/执行产品、数据库、测试、worker/engine child、网络/模型、GUI/native 或付费操作。静态检查仅文件/Git 原件读取、stdlib JSON/AST/hash/整数算式。

全文分段读取准备授权8800B、I05固定主稿219行、根独审168行、I05实施授权9754B、T01主稿全部章节及 supporting investigation/checks/budget JSON。AST库存整体JSON解析并逐函数位置核对，不把530项词法记录当530项动态执行或全部费用闭包。AGENTS/common身份等已读当前规则；本任务只读取相关固定方案与实际源切点，不读取I05新实现、C2或dispatch WIP。旧dispatch独审报告不变。

| 本轮 r1 原件                                                             |  bytes | SHA-256                                                            |
| ------------------------------------------------------------------------ | -----: | ------------------------------------------------------------------ |
| 主 `docs/iterations/T01/profile-job-artifact-selection-supplier-plan.md` |  67555 | `09d25b0c86cb3b51da592851b0d9d83da624917532dadb5a55dd13e4cee137bd` |
| `source-manifest.json`                                                   |  83877 | `a0e55c010c983e8c4a38536a53188456604036e44a593696a095ba9a0e3941fd` |
| `static-call-inventory.json`                                             | 601708 | `db6e522751c19411910d79f0e24eb9a39f77e776f0d2f95a9fd2e1b2290dd220` |
| `budget-quanta.json`                                                     |  11283 | `edbc7ff2b4c3ab3a950c12d6ff8803be45b668de48886a86f05e650dd7fab7f7` |
| `investigation.md`                                                       |   5164 | `ca6cee6375c48786fea6aba2189e163455897e27671aca94d213cc56685f3b28` |
| `read-ready-checks.json`                                                 |   2167 | `150e3d4af32de1e32f53bab4f682e538f122e407774b2962f196635745dc3a5a` |

后五项同本报告父目录；这些是输入原件身份，不包括尚未存在的本报告自身hash。授权和固定依据：

- 根 `T01-I05-profile-supplier-contract-preparation.md` 8800B/`8957aa0a482d6ead8b7426d0ebf13b5d4faedf3f9ce156b17ad44d6997acdcad`。
- I05主 `docs/iterations/I05/formal-producer-and-selected-integration-plan.md`，固定 `a3592837d854628948ef4c468b6c839f21763273`，69523B/`23a4ae9f7974185db61664fb1db892586140ea20995f1bb5950943717bd0ed4c`。
- 根 `I05-controller-formal-producer-selected-plan-prereview.md` 35841B/`ac6934f2b2e842aad90cba252835629064ae4ee06452892f3f4f551a774c6909`；历史首轮不通过和后续方案层关闭归属分开。
- 根 `I05-producer-fullview-implementation-authorization.md` 9754B/`2517a322ab2952c1a9444a6963fc790935240a158e0647ce7b2a706461e75031`；根 `I05-producer-fullview-fixed-inputs.json` 38921B/`bb2519d2483297250a79df38a1abd71575c66b65e81be7b8509877d50ab61131`。
- AGENTS15852B/`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；common17891B/`e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`。

静态独立核验工具 `8ebb9b` 实际 exit0：135项 ref/path/bytes/SHA逐真实Git全部相符；15项固定文档current身份全同，有ref者逐current/Git核同；19源码blob的bytes/SHA全同，530个函数name/start/end和原41切点逐AST相符，错误0。旧树未安装I05部分路径是清单明确的现状，Git中可读不等本树已采用。135和15的身份已核实，不依赖作者自报的verified布尔。

## 2. P2-PS-01：三槽正常制品无法满足4096B rows-json

位置：主稿§11（第195–197行）和budget-quanta的K1/K2/K32正例。每producer target为payload-json≤61440、rows-json≤4096，B合65536；主稿明确实际N3并承诺完整字段/不改原投影。

实际固定源：3ef `semantic_execution.py`（32917B/`cc701dba39cdeb7f2ae281dfd4a9580b879b9e85f34d3c87a09a3414e7c32731`）的 `_ProfileProjection.value` :528–593把每个int编码成 `{integerHex:hex(value)}`；:715–735把**整个encoded payload**解码后按8192字符连续切为单字符串行，再编码完整rows。rows不是仅4KiB的摘要或另外简短表格。3ef `semantic.py`（52609B/`5a3a53fc79928a7aa7de280a8477541db4053ec9b2bec489bf28a2ad4e935549`）:1040–1054给每个mechanism child全部limits、budgetLimits和budgetUsage。3ef `quality/rule_profile.py` :116–137固定17个ProfileLimits字段；:155–161固定usage六字段。

可复现静态下界：只保三child中这三组必需字段；将所有实际int都缩成编码最短的0x0；删除其它child字段、定义、Catalog、所有真实规则/源/结果和其它top字段。这是**下界计算用的无效残片**，不是伪造合法L或喂生产器。其完整三child残片payload已4266B；对应最短单字符串rows为5026B。真实完整N3只能更大，因此4096B rows角色必拒，正常正例不能靠“实现后再证峰值”来修正这个逻辑矛盾。

本轮纯stdlib工具 `868833` 实际 exit0打印 `minimal mandatory fields only payload: 4266 rows: 5026 per child 1409`。重现仅需JSON编码和固定字段名：

```python
import json
names = ("input_bytes", "term_bytes", "source_bytes", "digits", "integer_bits",
         "temporary_bits", "rules", "when", "comparisons", "heads", "variables",
         "bindings", "firings", "head_occurrences", "trace_items", "output_bytes", "work")
limits = {k: {"integerHex": "0x0"} for k in names}
usage = {k: {"integerHex": "0x0"} for k in
         ("work", "input_bytes", "output_bytes", "trace_items", "firings", "head_occurrences")}
child = {"limits": {"recordType": "ProfileLimits", **limits},
         "budgetLimits": limits, "budgetUsage": usage}
encode = lambda v: json.dumps(v, sort_keys=True, separators=(",", ":")).encode()
payload = encode({"reasoning": {"mechanismBatches": [child, child, child]}})
print(len(payload), len(encode([[payload.decode()]])))  # 4266, 5026
```

影响：K1/K2/K32的“正常N3完整原件”目标全部不可兑现；K32角色h/n/E、T及cache/persistent数值虽然按声明数组算对，却不能作为合法完整制品的可行示例。不能删字段、改rows成摘要、放弃N3或只用空batch取绿。

最小修订：保B/Q/I05原硬界和完整原payload/rows公式，为正常目标选择成对可行的payload/rows上界，注明raw UTF8、rows字符串转义与分片的关系；重算相应h/n/E/T及display额外副本、cache/history/SQL/C2 footprint和H。不得把选定字节数当实际计算输出或手填L；未来仍须真实三rule API产物及±1、末字段、32个实际来源的运行证据。此项当前未关闭，待新稿真实delta。

## 3. P2-PS-02：private rows直接进普通发布路径会被拒

位置：主稿§7 :120–122、§8 :136–140，及§11正常链。主稿要求“完整rows”进入原_publish_job语义和原rowId/ordinal/排序校验，却没有冻结I05 rows到公开ordinary rows的转换。

真实断点：上述固定I05 rows为 `list[list[str]]`；423b `JobStore._publish_job`（87227B/`8896c3e30007e1dec04eaf47ae5bb5c33a1e9b3a1d016cb9165f99d8b4deeacc`）:1533–1547逐row调用 `_valid("row", row)` 并取rowId/ordinal。原canonical `packages/contracts/v2/schema.json` :2142–2179的row是exact object `{rowId, ordinal, cells}`，不是数组。即使给任一合法非空I05行 `[["..."]]`，直接调用现发布链在首row即失败，不会到成功原子事务。只提“原校验/完整rows”不足以定义哪份rows是B原件、哪份是展示副本及费用。

这不是要求复制matcher或扩大公开schema。应明确一个有限确定性adapter，例如按原行序分配稳定合法rowId/ordinal并把原cells作为cells封装；精确选择由作者冻结。必须分别保留：

- strict artifact的payload-json/rows-json原bytes、原digest和原序不变；strict reader不得拿公开封装反推/重算B或rowsDigest。
- ordinary display rows符合原cell≤8192字符、rows数量/公开分页/完整envelope预算；明确空rows和边界Unicode、重复ID/ordinal的规则。
- 封装、排序/编码、同Store普通payload副本、临时持有和GC额外费用均先预扣；与role B一起进入cache/总库增长，不能沿用仅B+Q+4096的小计而漏普通展示副本。
- consumer query/SHACL的输出O也必须定义同样的公开转换/输出形状，不因为producer修了转换而让consumer另一路仍失败。

真实转换点应在已申请T01 writer内、同一成功事务保存前完成；原6/17字段DTO、原canonical row/public methods均不必放宽。该项已发root/作者，r1当前未关闭。

## 4. 其余实质审查及需保持的护栏

### S1：所有K的consumer材料及定义确认

主稿独立给K0..32本consumer原snapshot的U≤16MiB、definition D≤8MiB；U不借旧producer Q、不借D，也不从query/oracle造事实。snapshot-records/1明确只认证当前原持久N3文本及新locator，承认rdf_snapshot.term的lower语言/规范化损失；原用户文件/映射原位置须真实源owner供给。没有声称从旧N3恢复用户原拼写。None/空串/语言/重复来源保留、typed完整RuleSpec的when/comparisons/heads/source/disabled顺序、definition digest排除自身、原Store版本和v3确认/accepted/current/historical/undo路径均有具体合同。

v1/v2/v3不混过，opaque旧值不认证新来源；namespace全当前/历史碰撞有限拒升级。真实create/_accepted_job同事务claim/context、原参数/快照互证、不补旧context和per-capability resolver的真实代码/锁/manifest核同均有可用原切点。formal_scope缺失明记not-recorded，内部真实Coordinator/JobStore切片不等I06正式权限，也没有以整个T01/native未完作为无限前置。

### S2：duplex/三流与工作限额

原coordinator:593–615确为stderr DEVNULL、写完stdin即close；:690附近complete后break并reader.stop。主稿明确仅新profile分支改为真正持久stdin/ack、stdout全部预定roles和complete后继续至EOF、stderr独立有界drain，正常exit0才保存；没有把旧行为误写成已支持hex。32768raw/65536hex/4096完整header/LF总69633与262144原frame界有算式；一未ack块、原deadline、错phase/Job/index/ordinal/完整length/hash、尾流/非0exit/late都在矩阵。

实现时必须把所有begin/end/ack、stderr读取/丢弃、错误和收尾的实际query/byte/work额度映射到T/H及独立不可侵占控制票；不能用role X之外的任意stderr或无限close等待吞掉已耗尽的业务票。当前是要求而非实际循环证明。原physical512MiB/120s不放宽，逻辑H1GiB不等RSS承诺。

### S3：原子来源、四表与历史保护

JobStore finish_read_job原外层事务→_publish_job→_transition是明确可扩展切点；原_publish_job先canonical后界的缺陷不能被新wrapper沿用。主稿请求深meter穿透原storage/job_store/format3，完整read-mode result/origin/roles/current/succeeded同事务，正常child终态与最终cancel/scope fence先于commit。ownership回滚外details侧写在新scope下禁用，已有Job失败/取消与“无半artifact”正确区分。

四表首选两payload+job/result各一state，拒孤儿、仅available→evicted；完整角色manifest、缺失/损坏/合法evicted区分。原immutable blobs/context/claim/details/L不GC，current/report保护包含source依赖，active/retired pins真实解除后才删角色。公开结果明确白名单而不展开私有projection/ref，尚待PS-02给具体rows转换。

与ontology采用同一catalog writer/descriptor、唯一迁移窗口，历史旧hash/CP/migration_id语义保留，旧reader拒新profile。具体合成descriptor/DDL/SQL/hash及两个方案的唯一实际版本仍是根批准的实施输入，不应当成此稿已有源。建议把“各role manifest”明确排除origin自身编码/hash：origin传输manifest在外层生成，避免origin元数据含自己的digest形成自指。当前不存在必须自指的已编码实现，因此此项是澄清建议，未另定P2。

### SQL前界与启动风险

稿中正确指出Store.**init**/_migrate/format3.validate、JobStore.**init**/_validate_job3在adapter前已扫描；必须在同conn最小catalog识别后、任何全历史正文读取前装真实cost门，不新开Store/替real._db/复制validator。旧ProjectHostReader._preflight :163–197仍用 `length(CAST(TEXT AS BLOB))` 聚合，不能单凭“SQL不把正文传Python”证明SQLite内部扫描/副本已预界。

建议将固定C2的metadata-only→预扣明确probe work→费用SQL→累计证据→body的精确顺序和独立probe guard，明确扩展至新profile startup及所有SQL前门。UTF8计量/portable unicode逐字符路径的工作量要事前封存；仅metadata SELECT执行后再看read_work或Python UDF收到整TEXT后收费都不够。主稿不应把“SQL先长度”解释成可免费调用原聚合。本轮没有执行SQLite，不将该提醒冒称当前新代码实际失败；实施合同固定时必须明确原有探测工作guard的具体消费方式。

### S4/S5：累计账与真实寿命

每artifact独立R_j、原N≤100和原17L一次16c，consumer受理先Σcap/运行Σusage、失败工作不退、slot(j,i)唯一；同Job closed/failed不能新开，重开只reconcile，新合法Job新受理而非免费借旧票。U/D、全部K完整恢复后发布，R临时对象向S/H实际转交同时保留，不把max单R或live0当全体释放。这些避免原SB/CPS类方案问题。

有限selection2、pins64、history256/results128、8+8MiB原始持久cell/32MiB全库/64MiB C2交集，原hard bounds及profile启用时未知writer拒绝/尊重Tail headroom均明确为待根批准工程政策，不偷设Q5业务容量。三份start/cancel/finalize floor隔离，8次retry另付；最大16事务入层的63控制槽（外3+15×内4）及cleanup不被业务耗尽挡是可实现模型。真实SQLite I/O失败不能假称in_transaction=False。

C2和dispatch仅固定方案引用，没有采用WIP或fixture生产来源。claim→原Job/context对账、marker null不等未受理，复制库不认证physical binding，scope/current权限由I06真实owner给。内部真Job链有独立推进步骤；永久drain覆盖engine/worker/三pipe/timer/task/native/view/retired，不以TTL、kill/void/pending0证明释放。

## 5. 独立算术与后续验收约束

纯stdlib工具 `a44432` 实际 exit0，逐固定restore_budget.begin:251–303源码公式独立重算17域max、32倍聚合，及K0/1/2/32的X/roles/h/n/E、ΣRcap和三池work，全部等原budget JSON。该budget blob为37478B/`593b2a832dd510063bb60d7b3d5526fbd6cf4dcba53ad9c513e82dbfdd77ef7f`。opaque_scalar541065216也等原opaque块实际封存常量，故把H逻辑票设1GiB有针对性，但不证明native/view/Graph/新freeze峰值已闭合或512MiB物理门可达。

r1 K32算术确为X5271552/r164/h196/n728/E13525720，S的V4210688/N_total96，t128时opaque17381724192；这是按不可能的rows角色目标作的正确整数计算，不是合法正例可执行证据。R聚合live-cap许可和worker/parent/library实际H是两个门；前者的大数不替代后者真实并持。当前K32 cache/history小计明确不含所有旧snapshot/context/副本/row管理项，不能当16/32MiB全库证明。

未来必须至少给真实确认定义→原Job/claim/context→单owned worker一次capture→原Store同txn→正常drain/关重开→新worker一次fullview→K0/K1/K2/K32实际query/SHACL的完整非空链。完整7/15/11、source最后字段/Unicode/None/空串、独立R及Σusage、全部C/T/S/H/SQL/持久/临时峰值±1、失败重开不清费、全部角色/尾流/取消/最后artifact失败、GC/current/report/source pin、公开白名单和旧6/17字段都须原件。不能使用手填expected/L或生产fixture权限补齐。原83/89/40/M1/完整FR/57P0、T03新源包/目标OS/真人/指定同版双模型/CI/正常develop仍保原门。

## 6. 首轮状态与下一步

PS-01和PS-02均未关闭，r1首结论暂不通过；其余上述合同方向可实施，但不是已供源码/已测资源或生产接线通过。作者修订应保当前六原件与本首审，出新真实bytes/SHA及逐项处置；本审只对实际新delta及交互复核，不预设固定轮数。没有新稿前不替作者判断关闭、不抢改共享writer或原dispatch报告。
