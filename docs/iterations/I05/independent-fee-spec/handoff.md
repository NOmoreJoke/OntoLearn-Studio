# 交T05与I05的后继载体和精确delta

当前交付仅独立费用设计。T05正在独审的 `3d8f4ee912f41bd03388322d29a9bfc0e7defe85` 及原oracle不修改；接收本新候选后，由root向两位原owner另发精确delta。本候选不授权任何产品执行/接线或其它树写入。

## 1. T05可消费的数据面

| 新字段/载体                           | 类型/版本/来源                                                         | 使用规则                                                                                                                                  |
| ------------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `per-id.items[id].inputStructure`     | exact纯JSON计数，输入0e42 SHA固定                                      | 仅字面结构，不是typed material/preimage                                                                                                   |
| `predictedAllocation.children[*]`     | rule_id、原ordinal、disabled、完整17限额；I:76/R:103                   | 可预登记expected数值；113项可算，Turtle一项rules接收调用合同未供应保持pending（另列canonical省略参数时默认dummy17L条件值）；不能造同次17L |
| `revalidationCaps`                    | exact公式3ΣW+203N+33ΣFcap+4ΣOcap，2ΣI/2ΣO                              | cap不是usage；disabled/dummy保分支                                                                                                        |
| `mathFacts`                           | 本作者从纯整数1/2/3 vs2独立手选的18格                                  | 可判数学真值，不包含matcher或预算准入                                                                                                     |
| `existingIndependentBusinessExpected` | 固定未审T05候选oracle路径、expected JSON pointer、完整文件和每值SHA    | 保完整图/matches/head/DAG数学expected独立可用，不因本窗fees pending清空；不是新批准需求/费用权威                                          |
| `currentInvoice`                      | 下界/完整上界/首耗尽stage/domain分别nullable                           | exact缺项保null，不能把unknown补0；既有“至少1”不可冒exact                                                                                 |
| `proposalInvoice`                     | `i05-fee-events/1-proposal`；具体E/G/M/C/T/R/D/S/H组                   | 事件公式可计算，逐ID完整数学event程序尚待补；不能把小账事件套到全部114输入                                                                |
| `authority`                           | 实际同次17L、planDigest、budgetUsage、issuer、held binding分别nullable | 由真实发点/原owner证据供应，不能由数学模型填；不能由source/package一致取代                                                                |
| `decision`                            | exact成功/拒绝/首错或pending，finiteRelation保全                       | 只有完整独立事件+限额+身份映射才resource判定，禁止总允许RESOURCE_LIMIT                                                                    |

新比较器需把业务数学、资源可判定性、关系约束、真实权威四条结果独立列出；不要用一个布尔遮盖pending。未知不是成功也不是自动拒绝。14个negative先证producer成功并保原expected，再receiver扰动；完整原摘要不变时应integrity拒，不能重签让tail错走深层。若要测深层首错，另用获准独立受损来源/受界内部阶段测试，明确其非同issue wire否例，不重用本14格标题冒深层覆盖。

## 2. T05必须供应的最小纯规范delta

1. 对M01…M04，逐字段 typed input/output/fingerprint 编码的字节文法、record tag/字段顺序/整数hex/nullable framing、全部重复位置；planDigest原前像精确字节与域。当前proposal TLV只作新proposalPlanDigest，不替代原编码。
2. 对E08/G01/M02，parse/check_value/compare各域的固定数学 primitive schedule或具有限域参数的 opaque BLOCK：十进Horner、幂、GCD、binary舍入、Calendar组件、IRI/lang/regex、source fingerprint逐发点。每primitive预付和temporary_bits上界要在运算前，bool拒int。
3. 为“至少1”项目选择本候选ITEM1提案或给另一个精确收费，逐definition/binding/comparison/head/proof/trace及字段/序列化事件；变动成本版本需显式owner/root接收，不回写旧机制已遵守。
4. 单个同child compile/eval完整事件集与三池完整重放事件映射；disabled definition-only与dummy空batch分别列。原limits及业务语义不提高、不删source/false/head。新增成本若超旧cap须精确报告冲突与优化方案，不上调cap取绿。

这些纯规范可以先独立供应；本窗不要求读取产品算法或运行探测来“找到expected”。收到规范后，独立作者可据纯输入/数学witness补齐每ID提案invoice；不能让真实usage倒灌为预期。

## 3. I05必要实施delta（只请求，不施工）

| owner/原边界                 | 具体待映射组                                                                                              | 后继验收                                                                                          |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| I05 input/canonical material | E01–E04/G01，原UTF8/source与preimage每重复出现、formatterBLOCK、控制/receipt初始化                        | source40000/None空串/重复source与alias、单项/总byte差1，预门在分配前                              |
| I05 graph/matcher唯一writer  | G02–G09；所有graph/index/hash/collision/sort/closure候选/union/match及失败loop独立数学收费规范            | 有穷纯规范动作表先供，再核真实发点逐loop；不第二reason、不改变首witness，全部false后比较/allheads |
| I05 capture/project/fullview | C01–C04/R07/R10，完整7/15/11或7/16/11、17L/usage原发点保存、whole-J五摘要+Catalog/完整freeze并持          | C64/63、stage6摘要前4M、最后字段失败、no prefix、旧native仍活时先reserveview                      |
| I05 restore/cache            | R01–R09，多域A1…A16、完整key49B、两投影全部PV/重复Catalog/top-child、整数hex、原前像、R_parse/16c各自一次 | 每域exact/差1、cachehit仍逐值核、碰撞全key/共同prefix、末child拒且不重开                          |
| I05 directsteps/roots        | D01–D04/S01，全部候选8/step32/key16+2含覆盖证明、真实link、alias identity/DP、全root occurrence           | 重复候选/late-shorter/全heads/重复targets、最后premise/depth/leaf、whole-J而非ΔB、Dr临时DP并持    |
| T01原owner后继               | T01–T02/S02/H01，真实Job/expected/17L来源、K0…32独立R_j/Σ、sender/receiver/retired/permission/GC          | 真实受理/保存/重开/worker终态/撤权、同Job禁新ledger重试；不以H逻辑票代物理RSS                     |

每个函数/文件实际写权须root下一窄窗口按原ref/bytes/SHA授予；本表不取得quality、shared Store/canonical/worker、四build/lock或T05受审候选写权。原cap、五operation、32全部分支、原业务83/417验收不缩减。产品字节变动后按原门重新独审/验证；本窗数学自测不替产品测试、source/package、CI、两OS或真人。

## 4. 精确剩余

当前0个完整现行114-ID invoice可定值，113个完整17L预测、18个独立整数真值、全部114的结构/外部expected指针与conditional关系可使用。缺的是可前瞻计算的完整typed字节/算术/图动作schedule和真实同次权威。仅有C/R/D上界不能保证所有输入在旧池内，也不能确定哪个资源先拒。后继必须补齐这些缺项，禁止把本设计冻结称“完整收费oracle已过”或把所有RESOURCE_LIMIT接受为结果。
