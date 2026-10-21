# f68c7516 方案独立 schema / 预算 delta 复核

结论：**修订方案在本审schema/预算范围通过，原SB-01[P1]、SB-02[P2]、SB-03[P2]均关闭；未发现新增的P1/P2合同反例。** 这是docs方案结论，不是supplier已存在、预算已对实际新代码证明或完整producer/selected已运行通过。

## 固定输入和方法

- 本稿ref `f68c7516c6ea96a2655c3aef2d89abd749f5d805`；首稿 `651c4c2d2dd498ebc572543d116f2cdddb678045`。
- 主方案69441B、219行、SHA-256 `0d866d896224eb82abfe3d87537f10b7671c7eff068c0e0a6015f9698b55d9e6`。本次已全文重新分段读1–219，并对照651c→f68主稿Git diff；未只查关键词。
- 全文读固定`counterexample-dispositions.md`；原首审报告/输入、授权与root closure继续适用且不改写。当前AGENTS SHA仍`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。
- 复核实际T01 C1 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`的_dependencies:758–773，结合已读create_job:895–898核same snapshot/kind/available/manifests/implementation；没有把新文字当现存接口。
- 135拟closure本身与首审逐字未变，首审已逐Git hash核同；此次两ref差异均为docs。静态入口词法清单只作定位/元数据，不当动态调用完备证明。
- 输入bytes/SHA、docs差异路径和算术在`delta-2-inputs.json`。未import或运行产品、SQL、组合探针、worker/native/GUI/模型/付费；未采用/提交/发其他聊天/操作Goal。只写本审新delta文件，首审原件保留。

## 旧意见的实际关闭依据

### SB-01：K=0与所有K的consumer真实图及费用，关闭

68、114、134现在对所有K明确独立`consumer-input-preimage/consumer-source-preimage`，由**本consumer**实际snapshot owner在受理前固定assertedRecords/ontologyRecords、source、parser/options及Job/op/scope/vector/manifests身份；不是若干producer旧输入的并集。U≤16MiB，input/source各≤8MiB，Turtle原1MiB门不变；definition/query/shape另D≤8MiB。

对首审/根共同K0反例逐步代入：选择数组空但consumer snapshot含一条事实/公理时，仍接收U；U是显式canonical物料，即便明确空图也U>0。parent准备使用独立C（Q换U、N=0）；双方T计U收发与副本；153的S基础量变为`V=U+Σ(B_j+Q_j)`，故K0的scan/copy=64U、scalar=16U不再为零，codec/词法/term构造均要求S事前付。163明确K0直接从该U建只读scope、不调reason/R_j，165又禁止producer input代本次图；180将U/D parent pin、raw/encoded、worker Graph逐owner计H。原“无role/零费用”执行矛盾已消除。

151的传输算术独立核算：production Q16+D8+B8+P16=48MiB；selected K32为U16+32×(B8+Q16+P16)+D8+O8=1312MiB，K0≤32MiB。producer raw40MiB与consumer U/D是分开的量，未漏加U，也未把累计1312MiB当同时内存。raw再hex编码、header/ack/control经h/n/E另计，不把1312MiB直接当encoded总量。完整envelope标点归4096 header，5K+4角色manifest分role-begin，未再先塞一大frame。

206/207/210的未来验收同时补K0非空query、SHACL通过/违规、空图、U/source/ontology/尾片/身份污染、实际非零费用；不是只增加一个“K0”词。

### SB-02：per-artifact R_j和consumer不可重置聚合账，关闭

144、155、163已经一致规定：每原artifact j一份独立pure R_j及其原B_j/Q_j/N_j/L_j，一次new→running→terminal；consumer另有外层聚合费用/持有账，**不复用终态pure ledger、不合并payload、不把N_total≤3200塞进N≤100、不重新divmod**。

因此K2/N1+N1反例现在执行两个不同R_j，第二次不会因复用第一个terminal失败；这不是向同artifact重领预算。K32也只聚合费用和持有，而非改纯schema的N门。155要求受理时从可信长度/原allocation计算每域Σcap、核真实owner有限job quota，运行前阶段预付，累计Σactual_usage及(j,i)原term parse；失败/切换/重读不退款，聚合不足在潜在超分配前拒。

串行R临时和已转交view/图/索引并持分开：不能用max单R峰值代表全部S/H，转交先同时预留、再实际drop未转交部分；全部K/全child通过才提供scope。163明确C/T/R聚合/S/H都不因切换清零。

16c累计边界也已明确为`Σ_jΣ_i(3W_ji+k_ji), 2Σ_jΣ_i I_ji, 2Σ_jΣ_i O_ji`，`k_ji=203+33F_ji+4O_ji`。按K32、每artifact既有整次池及N_j≤100计算，静态work上界1645898112、input/output各16777216逻辑单位/bytes；这只是公式代入，不是假称N100已成功生产或实际quota就是该数。原N100资源失败证据不变。

167同Job只复用活跃handle；worker死亡/取消走原终态，无隐式重算；新operation重新受理自己的配额，不借旧Job或跨Job缓存跳核验；关闭重开后的非terminal依真实reconcile，只有新合法consumer Job再恢复一次。180缓存键补consumer Job/op/context/U/D，重读边界与费用合同相符。K0无R_j/16c但C/T/S/H照付，亦已显式。

### SB-03：完整保存树字段族，关闭

79及84现明确外payload七字段、reasoning十五字段、mechanismBatches每child十一字段，保planDigest/limits/budgetLimits/budgetUsage，不用allocation或旧RestoredChild补造。对首审“读最后budgetUsage.work/planDigest”反例，这些现在有明确字段位置和原值保存合同。

新frozen record与list→tuple视图保schema原容器位置，native叶值/None/exact int/bytes/source逐字段保留；旧children只作16c事实视图。raw rows继续独立原bytes验证，不从view重算。原native必须仍可达、safe树释放后先预付再freeze；没有先drop后重新parse。完整字段级无损signature与原canonical payload/rows核同、11字段对象/标量并持及receipt/异常locals的新R/S/H证明均为接收前门。206的验收指明完整15top/11child（含planDigest/budgetLimits/Usage），没有退回只测selected输出或hash。

## 新delta一致性与保留门

- **原真实请求门保留**：161与423b源码一致，selected kind=reasoning、same inputSnapshotId、payload available、重叠manifest一致及完整implementation同一。historical使用其对应原historical snapshot，不以“兼容”放行V1→当前V2。U的consumer身份不能靠一个同snapshot字符串绕过完整source/definition/参数/code manifest与permission校验。
- **未改原机制**：128及155继续保持原B/Q、N、原17L整次W/I/O/F等、每原child一次16c；原seven机制与pure budget默认只读。C/T/S/aggregate新增计量不是修改纯cap或原L授权。
- **准确区分待实施证明**：C八阶段、T h/n/E、R_j fullview freeze及聚合收费时点、S的RDFLib词法/值/Graph索引/碰撞最坏块、H全owner/retired/persistent quota仍须最终源码逐loop/委托/并持与低限±1证明。没有supplier代码时，本审不把公式当已完成数学或CPU/RSS容量证明；也不将明确尚未实施本身报成方案缺陷。
- **实际供应仍未齐**：T01 S1–S5、typed private context/protocol/schema/migration、物理/current scope、T05数学/解释、T03同一真实Job包、窗口/目标OS/真人/指定双审/CI等仍是原精确门。根须另批writer/采用与代码窗口，docs通过不能替代它们。
- **非阻断措辞说明**：157的“per-job最大原物料48MiB”应按151明确的production语境解释；实施配置不能据此给selected累计设置48MiB并宣称支持该上界。建议未来供应说明写成“production单次准备物料48MiB”，但151已分别明确production48/selected1312/K0 32，故本审不据此重开P1/P2或认定预算公式互相覆盖。

本范围无未关闭的方案阻断意见。首稿不通过结论与原hash保留，当前通过只绑定f68完整稿；未来实际代码或schema/预算/供方基线变化仍需相应新候选验证，不能直接继承本方案通过。
