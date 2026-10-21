# 651c4c2 方案独立 schema / 预算审查

结论：**当前方案不通过，需先关闭3条具体方案意见，再授权实施。** 这不是要求现在实现尚不存在的supplier；问题是本方案对已明确支持的K=0..32、纯恢复ledger及“完整top projection”存在相互不兼容的合同。C/T/S实际逐loop、低限、opaque与并持证明仍是合理的实施前门，不能用方案公式替代，也不因代码尚未写出便报为漏洞。

## 1. 身份、输入与静态边界

- 固定ref `651c4c2d2dd498ebc572543d116f2cdddb678045`（解析自651c4c2）。
- 主方案 `docs/iterations/I05/formal-producer-and-selected-integration-plan.md`：59605B，SHA-256 `fe28f883c1db687b4c20da4f91046d66216fcb4322a43633306af159a9cb861f`，全文213行已读。
- 全文读当前AGENTS、根授权（主checkout `iteration-control/2026-10-21-weekly-release/I05-formal-producer-and-selected-integration-plan-preparation.md`，6107B/SHA `3d707e0844e4302f5bbdf62e51fdb790737df1e690127c451fc20f47feadfa42`）及root closure原件（3306B）。根授权的160旧交付/全部产品只读、纯docs/不运行/不采用、唯一owner边界适用。
- 阅读3ef固定semantic生产捕获点、restore返回结构/child字段、budget单次状态与N界、legacy selected图构造的相关源码；阅读T01 C1 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`实际derivedResultIds schema、create_job与worker相关接口。支持调查仅作定位，未将其中旧base64建议当主方案lowercase hex协议。
- 拟初始closure135项逐项Git bytes/SHA全部核同；这是静态来源核对，不是采用、组合可运行或API兼容通过。2同字节overlap与resources不同来源冲突仍由原owner/root在实施前处置；主方案已明确该门。
- 输入ref/bytes/SHA、135项hash结果和静态反例参数在`static-inputs.json`。没有product import/执行、组合探针、worker/native/GUI、模型/付费、他聊天发送、Goal、commit或产品/旧160修改。只写本审目录。

以下行号均指上述固定主方案，代码旁证另注明固定ref。

## 2. 方案意见

### SB-01 [P1] K=0合法请求没有覆盖真实图物料的S预算

位置：方案130、142、149、155、159；真实入口范围旁证为C1 schema `derivedResultIds` minItems0/maxItems32。

方案明确K=0是合法asserted-only，且S负责“完整原input/ontology”的遍历、RDFLib值构造与只读scope建立。但149定义 `V=Σ原结果(B_j+Q_j)`、`N_total=ΣN_j`。K=0时两者严格为0，普通scan/copy cap=0、scalar cap=0；仅objects4096和Graph.add opaque扫描块非零。

具体反例：consumer是合法asserted-only query/validation Job，选择数组空，snapshot含一条普通事实或一个ontology公理。建立该图仍需读词法/来源、构造RDFLib term/graph并持有其载荷。即使t=1，普通S的文本扫描与scalar票仍是0；Graph.add opaque工作不能跨域支付普通值构造与持有。不是CPU/RSS反例，也不是要求该请求一定成功处理100000图。

传输方向同样未闭合：130的selected parent→worker仅列每个原结果的origin/payload/rows/input/source和consumer-definition。K=0时没有任何原结果输入role，文档没有明确consumer当前asserted物料怎样到worker；禁止子进程开第二Store/path，因此不能靠它自行取图。如果意图将asserted/ontology放进consumer-definition，必须明确该role的完整schema/来源/长度，而不能只以“定义”一词默默容纳事实。即使该role能含图，S的V仍未纳入它。

必须修方案：定义consumer自身asserted/ontology物料及完整来源/role，给K=0明确执行路径；将其bytes/节点/term/来源计入S的基础量，并同步T的X/E、H/raw+encoded/live及每role上限。也可明确K=0由已有consumer图构造路径支付，但需列其实际唯一预算与接口，不能让S表继续声称支付全部input却数值为0。新增物料后的1296MiB累计传输上界也要重算，不能只补文字“另计”。

### SB-02 [P2] 多结果恢复的ledger粒度与累计费用互相矛盾

位置：140、155–157、161。旁证：3ef `semantic_profile_restore_budget.py:251–259,388–397`，`RestoreLedger`只能new→running→terminal一次，N≤100；pure入口也拒terminal复用。

140写每consumer原Job“一次operation ledger、全部原N槽”，而157对每原结果j建立独立expected/allocation并调用一次restore_profile_result，保持各自N_j/L_j。此处一个consumer可K=32。

具体反例一：K=2，两原结果均N_j=1。若按140只给一个现有pure ledger，第一restore完成后state=success，第二restore复用必拒；若将两个artifact当一次B/Q输入，又破坏各自摘要、source witness、原allocation和现有单artifactAPI合同。

反例二：K=32且各N_j=100时N_total=3200，无法塞进现有N≤100 ledger；把3200槽重新divmod又违反原L不重分池。这里不假定N100当前存在成功生产见证；这是所宣告schema的静态组合上界，K=2/N1已足以说明矛盾。

必须修方案：明确每原artifact恰一个独立pure R_j ledger及原slots，consumer原Job另有不可重置的**外层聚合费用/持有账本**，不是冒用一个纯ledger；给聚合R域的Σcap/Σ实际usage和串行peak/已转交S/H持有来源。16c也给Σ_jΣ_i(3W_ji+K_ji)、2ΣI、2ΣO，不跨结果重分池。K=0时无R_j/16c但仍有consumer自身S/T/H。失败、重读、切换原result与新operation分别怎样扣这两个层次需一致。157只写C/T/S/H累计不清零，没有把R聚合解释清，不能以32有界代替账本合同。

这是方案合同矛盾，不是批评独立R_j重新领其合法原artifact池；原结果之间各有独立真实生产W/I是正确前提。

### SB-03 [P2] “完整top projection”漏掉mechanismBatches字段族

位置：77、157及200。旁证：3ef `semantic.py:1090–1118`的top result；restore `RestoredChild:140–149`及`_Decoder.child:783–829`。

77承诺冻结已严格校验的“完整top projection”，却只枚举rdfs/rules/warnings/evidence/rdfsEvidence/firingGroups/defs/Catalog/proofLeaves/termSources/graphBudget及格式身份，没有mechanismBatches。3ef原top中该字段包含每child 11字段：ruleId、definitionOrdinal、disabled、planDigest、batch、originalMatches、definitions、catalog、limits、budgetLimits、budgetUsage。

旧RestoredChild只保rule_id、ordinal、disabled、defs、Catalog、original_matches、batch、fact；不含planDigest、limits、budgetLimits、budgetUsage。原allocation可证明/重取limits，但不能由此恢复保存时budgetUsage或planDigest；用reader外部context补值也不是冻结原完整top。不能把“child native类型不变”当作已保存这11字段。

具体反例：读回一个真实child的最后budgetUsage.work、planDigest，或对完整top字段做精确签名。仅按77枚举的view+旧children，不存在这些字段。它们在decoder虽已严格核验，native树释放后就不可从返回接口读回；两份不同保存字段会映到同一返回view，从而不能满足200“完整native签名/原L/...完整读回”的声明。

必须修方案：完整列RestoredProfileProjection/1 top字段及mechanismBatches冻结schema，保11字段的原类型/顺序/None/整数值，说明既有children是机制事实视图而不是保存树的替代；对该fullview定义无损、字段级roundtrip/签名验收。新增freeze的scan/copy/objects/scalar与异常locals须计入新R/S/H证明。若确实只返回selected专用子集，应更名并另保可完整读回的strict原投影接口，不能仍称完整top且靠再次无账parse补字段。

## 3. 已合理闭合的部分与实施前门（不另报方案漏洞）

1. 同次真实producer切点清楚：L在实际ProfileLimits创建点、defs/Catalog在规范化点捕获；只有一次reason和一次原projection/rows。前像由真实受理owner在计算前固定，不从payload/机制组反推上下文。16c仅supplied-batch consistency，pure formal_authority=False不改；完整图可信性依实际producer/Store原事务。
2. fullview方案明确复用同decoder/API core，不让selected重parse raw；list→tuple是新视图、旧wire不回写。A16新freeze≤J/≤2J的数值本身不是证明：必须列实际freeze位置、保留scalar/objects、与safe树/receipt同时集合、失败公开frame清locals，以及同原cap/新schema版本的实际delta审查。当前已写为实施前门，不能直接说3ef已证明新API。
3. B≤8MiB、Q≤16MiB、P≤16MiB、D≤8MiB及原W/I/O/F/disabled槽有明确分域。production最大raw48MiB、selected现公式32×40+8+8=1296MiB的算术正确，但SB-01新增consumer物料后必须重算。累计传输与同时内存不混同。
4. lowercase hex chunk32768→65536，header≤4096+LF所声称69633<262144；供应实现需把引号/keys/分隔/完整envelope都计入该header口径，不能只界一个header对象后漏data framing。ordinal/role/phase/result index/unique end/增量hash/一个未ack块及deadline不重置均需T01 canonical冻结。目前这些是请求而不是现成wire，未把旧worker test ready当真实制品通道。
5. C固定8阶段×16J与T的h/n/E、S的Graph.add opaque块，需要实际supplier逐调用/循环/库委托/输入schema和低限±1证明。尤其RDFLib值构造、hash/碰撞比较、lexical解析/复制、Graph索引、排序/去重、query/SHACL算法分别不能互借费用。没有源码时不能声称公式已覆盖全部内部实现，也不能凭大cap称通过。计划151已保留该门，属于实施前证明，不因尚无实现而另报缺陷。
6. H已区分历史metadata不可GC与派生cache、active/retired、T01 pin/worker/pipe/source和I05 native/PV/view；transfer先双留票、实际drop/终态再降live，失败不退累计work。历史quota由root/T01冻结、未配置关闭正式准入，避免给Q5默认答案。需未来实测，但此docs阶段没有伪称已有真实账本。
7. T01 S1–S5、T05与T03 owner路径/现有接口缺口已明确；52组件与135闭包均未采用，资源冲突没有整体precedence遮蔽。新Job context/protocol/origin/typed公开白名单/旧库版本拒绝都需T01唯一schema供给；旧result.page只display rows，不能供应strict原bytes。这些不能被I05自写第二Store/receipt绕过。
8. source/definition/Catalog/参数/implementation/actual锁+完整code manifest的字段组充分标识所需来源类别；完整私有typed schema、nullable/长度/版本错误、request兼容矩阵、current/historical scope与definition/参数兼容判定仍须供应冻结。未冻结时接口不启，不用“same version字符串”代内容身份或物理权限。
9. K=0/1/2/32、duplicates/33、末result/末child失败、GC/撤权/retired、完整字段污染、原83与数学解释、source/package真实Job验收矩阵保留；不能用旧145/23exec充新链。不自动把四资源失败/一缺规则归因T01，也未擅改oracle/L或删source/false/head。

## 4. 处置与复审范围

先修改SB-01的真实consumer图物料及计量基础、SB-02的per-artifact R与consumer聚合账本、SB-03的fullview完整字段合同，同步供应表/新writer/预算与验收行，冻结新docs SHA后做必要独立delta复核。无需固定三轮，不在本次授权下执行产品或组合试验。

本审不替来源/生命周期另一独审，不替指定双模型、CI、目标平台/真人或根最终实施批准。本次只证明固定文档存在上述合同矛盾，未产生任何新运行、CPU、RSS、完整producer或selected成功证据。
