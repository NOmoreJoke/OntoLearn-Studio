# I05 正式 producer / selected 方案：完整修订稿来源与生命周期 delta 复核

结论：**方案层有限通过，OL-1关闭；未发现本次完整修订引入新的来源或生命周期阻断。** 该结论不接收尚不存在的产品实现、135项采用、预算实测或正式生产权限。首审651仍是不通过原件，没有倒写其结论。

## 固定对象及实际读取

- 修订候选：`f68c7516c6ea96a2655c3aef2d89abd749f5d805`
- 父候选：`651c4c2d2dd498ebc572543d116f2cdddb678045`
- 主方案：`docs/iterations/I05/formal-producer-and-selected-integration-plan.md`，**69441B / SHA-256 `0d866d896224eb82abfe3d87537f10b7671c7eff068c0e0a6015f9698b55d9e6` / 219行**。
- 本审已全文重读219行及反例处置表，并核651→f68完整差异；没有仅按新增关键词判关闭。原授权、实际T01/3ef/C4源码输入及第一轮判断保留为必要上下文，不扩大重新探索产品源。
- `delta-2-inputs.json` 固定本轮输入ref/bytes/SHA、完整差异SHA与hunks、原审原件身份、实际schema字段对照、29文件241处静态inventory逐行/hash核验。当前主方案逐字等于f68。135拟闭包文档与651逐字相同；4be→f68的全部Git差异仅在新方案及其新review前缀，旧160未变。

## OL-1关闭：按原非空K=0反例逐段核对

首审反例是：真实consumer Job C的原snapshot S有非空事实和本体，query/shape definition自身不足以构图；K=0没有任何producer artifact，所以原穷举role合同无法把S送给新worker。

修订现在给出完整且连续的供应路径：

1. **原内容与原owner**：第68行新增 `prepare_selected_material`，由T01原snapshot owner在consumer受理前固定本次Job的 `assertedRecords/ontologyRecords` 与完整SourceRecord；consumer input/source独立U，query/shape及相关定义独立D。没有用producer旧input的并集、expected、oracle、query文本或重新reason补事实。
2. **不可变受理绑定**：第68、114行将consumer U/D的版本、snapshot/public-internal project、operation/Job/scope、vector/manifests、parser/options、完整role长度/摘要/引用纳入T01 typed受理context。它们仍须由真实owner发出，不以任意外部JSON或成功布尔供应。旧六字段DTO/旧Job不改写。
3. **实际可表达的运输合同**：第134行对所有K都列出 `consumer-input-preimage/consumer-source-preimage/consumer-definition`；与每个producer的五role分开绑定。K=0时仍有完整consumer输入，worker无需开库。第151行要求role-begin有界传递，不能用大清单绕过帧前门。
4. **唯一基础图**：第153、163、165行明确基础asserted/ontology只从本consumer U一次构图；producer input/source只用于原推理复核。K=0不调用reason或R_j，也不因为没有producer就省略decode/词法/term构造。K>0只将经验证的RDFS/head按scope分层加入，不重复注入producer asserted。
5. **费用与持有跟随实物**：第68、151、153、155、180行把U的parent准备、双方运输、worker图消费及parent pin/raw/encoded/native/Graph均列入C/T/S/H；K=0的canonical物料仍有非零U，不能再以V=0使实际工作免费。具体逐操作和库委托证明仍在实施前门。
6. **正确验收而非仅拒绝**：J02第206行新增K=0非空query、SHACL通过/违规及明确空图成功路径；J03/J06覆盖错consumer snapshot/ontology/source/尾片、K=0非零费用。正常违规须真实报告，不能把所有K=0都有限拒绝便当闭环。

因此，原“C只收到definition、没有S内容”的反例在修订合同中已被排除。这里关闭的是方案表达与责任缺口，没有运行query/SHACL或宣称U供应已存在。

## 其他修订的来源与生命周期复核

| 修订面                     | 实际核对结果                                                                                                                                                                                                                              | 未关闭的实施门                                                                                                                          |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 每artifact恢复与原L        | 第144、155、163行给每个producer artifact一个独立一次R_j及其N_j/L_j；consumer另有不可重置聚合账。不会复用终态pure ledger、将K×N塞N≤100、合并payload解析或重新divmod。每child仍一次同原L，(j,i)身份唯一。                                   | 新fullview的实际R_j delta、聚合quota前门及Σusage/同时持有均须按最终代码证明和低限±1验证；不能因本方案通过提高3ef cap。                  |
| 同Job复用/新operation/重开 | 第167行收窄为同consumer Job仅复用同一活跃handle，不重开R_j/聚合账/三池；worker死亡/取消按终态处理。重开原非terminal按T01 reconcile，只有新的合法consumer Job才新受理/收费。                                                               | 必须由真实claim/Job和active owner约束，不能由caller新建operation或ledger洗掉旧累计费用。C2对账与永久排空仍待供应。                      |
| cache身份及释放            | 第180行新增consumer Job/operation/contextFingerprint/snapshot/U/D/完整有序选择/permission generation；命中仍核完整identity、origin和权限，不能跨Job跳过一次核验。第173–178行原fence→实际terminal→释放规则不变。                           | role pin/GC、全部active+retired、父子actor独立持有及撤权race必须实测。当前TaskService detach或Engine.stop不能替代这些门。               |
| current/historical         | 第117、161行明确保423b现有same inputSnapshotId、reasoning kind、payload available、重叠manifests一致和完整implementation相同门。historical选择相应原historical snapshot，不把V1推导混入当前V2；来源/代码身份继续更严格核。                | 放宽现约束只能canonical owner/root另行版本化批准；本次没有改变产品决定，也不把新普通历史读取当正式来源认证。                            |
| 完整projection             | 第79、84行明确payload7字段、reasoning15字段、mechanismBatches每child11字段，保存planDigest、budgetLimits、完整budgetUsage，不从旧children/allocation补造。native仍可达、safe树释放后预付freeze，完整字段级signature及原payload/rows核同。 | 尚未存在fullview API；新record/container映射、receipt异常局部、所有metadata/强引用并持必须实际审查，不沿用3ef旧返回结构假装完整。       |
| 事务及正式来源             | 第45–52、90–106行仍是原受理Job/claim→唯一计算capture→同Store artifact/origin/result/terminal事务；consumer U新增没有引入第二Store、worker开库、任意expected或外部权限位。                                                                 | T01 S1–S5、真实source/typed规则确认、事务内最终cancel/scope/权限fence、I06 physical/current_scope仍待具体供应与验收；正式入口继续关闭。 |

独立静态字段核验：用标准库AST读取固定3ef恢复模块的 `_PAYLOAD/_REASONING/_CHILD` literal表，与新方案第84行三份exact列表逐项、顺序核同，结果为 **7/15/11全部相同**；没有import或执行产品。29文件241词法hit的原行文本及文件SHA全部等其固定3ef；包含非调用位置，故它仍只是定位清单，不证明全部动态调用或alias已覆盖。

预算相关仅核本次物料是否被遗漏、归属是否一致及基础算术：第151行 `32×(8+16+16)+16+8+8=1312MiB`，K=0为 `16+8+8=32MiB`，与独立U及producer B/Q/P、consumer D/O一致。该数是累计raw角色上界，不是单帧、同时内存或容量通过线。第151–157行仍保encoded/header、分actor、live/retired、逐loop/库委托/配置quota的证明门；本审不替预算审者对尚未实现C/T/S/H作源码证明。

## 格式证据更正与原件保全

此前首审执行默认 `prettier --check` 得到exit0，但当前 `.prettierignore` 明确忽略整个 `docs/reviews`，所以该命令没有证明首审报告和输入清单自身符合格式。首审“格式通过”的表述应按此更正；来源/生命周期反例及原文件身份不受影响。

本轮显式 `--ignore-path /dev/null` 检查首审两文件，实得exit1，两者均有格式差异；stdout/stderr/命令及原文件哈希保存为本目录 `delta-2-first-format.*`，不清洗原件。首审report仍 **14767B / `7e35c4bf6bebea298c7c132a1a7f00af410cc553ed519eb52c515c31a5f13cf9`**，输入清单仍 **62034B / `f312a36fc66be5f6f9ef6490641c9dfae5fe294403e16f713fba7c6b144c66f3`**。按明确保全要求没有覆盖格式化它们。

delta新报告、输入清单与新增JSON回执均另用 `--ignore-path /dev/null` 实际格式化/检查；其结果另存本目录delta-2格式回执。该检查只涉及自己的新文档，不扩为产品检查。

## 有限出口

`counterexample-dispositions.md` 对OL-1/根K=0的“方案已修、待独立delta”状态有实际合同支撑；本审据完整修订判断 **OL-1可在方案层关闭**。新R聚合、fullview及供应门的完善没有引入本范围已证实的新来源/生命周期矛盾。

本轮仍只有静态Git/文件/JSON/AST/hash/文档格式操作。没有产品import/run、SQL、组合试验、新worker/环境、135采用、模型/GUI/native、其他聊天消息、Goal或提交。各supplier真实实现、逐费用证明、同一真实Job源/包/selected/生命周期实测、完整父I05/57P0/目标OS/真人、指定双审/CI/正常develop/远端均未关闭；必须由根后续精确代码窗口和原owner推进。
