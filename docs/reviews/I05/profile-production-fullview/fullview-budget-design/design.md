# fullview 最小共享decoder设计与预算建议

结论：**在e446采用的原restore/budget合同内，有可实施的最小路径，无需先改只读budget cap。** 建议在原safe树释放后、A16前票通过后，直接冻结仍可达的raw外层metadata与native reasoning；只生成不可变容器，复用严格验证过的不可变叶，不再JSON/hex/UTF8编码。新增ordinary objects先留2J，建议另留scalar4J作为完整view保留/转交的显式保守块。实际源码必须按最终构造式重新核逐操作、峰值与失败引用；本件不是新代码通过。

## 固定输入及本次边界

- 工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration`；adoption `e4460763890cf9550f359395df83260d75fe2e0a`；base5f。
- 原restore：50276B / SHA `aa3d51c1ccc487ce21a78560ad6cdf7a6485cc86f746c29ee329e6a0bc4c4d09`，1272行；budget：37478B / SHA `593b2a832dd510063bb60d7b3d5526fbd6cf4dcba53ad9c513e82dbfdd77ef7f`，1120行。以下行号只指这份固定Git源码，不指正在施工的工作树。
- 全文读根9754B授权/SHA `2517a322ab2952c1a9444a6963fc790935240a158e0647ce7b2a706461e75031`，新inputs的AGENTS/common（含完整第九节）、fixed-inputs全部JSON条目；135采用逐Git bytes/SHA核同。详细来源在 `inputs-and-static-checks.json`。
- 只做静态Git/text/AST/JSON/hash/算术；不产品import/run、测试/探针/环境变更、GUI/native/模型/Goal/其他聊天/commit。只写本设计前缀，不与root的restore/two-tests或另一agent的producer路径争写。
- 一次静态清单脚本误读字段files而发生KeyError，已保留摘要；正确字段initialExactAdoption重读核135项通过，无产品执行。

## 1. API及唯一计算/恢复路径

建议公开私有组件入口保持同形参数：

- `restore_profile_batches(payload_json, rows_json, *, expected, allocation, ledger)`：原exact返回RestoredBatchSet/字段/错误合同不变。
- `restore_profile_result(...)`：同样仅接exact bytes和原exact context/ledger；返回新frozen `RestoredProfileResult`，持有 `batches: RestoredBatchSet`、`projection: RestoredProfileProjection`、`rows_json: bytes`。rows可直接保原入参引用，不重算。原payload bytes由调用者已有，不强制新增第二份。
- 两入口调同一个内部operation/decoder/API编排；fullview模式只由两个固定入口传内部bool/enum，不开放用户callback、mapping、native-result替代输入或外部factory。
- 新projection/result另设私有输出版本，原input schema/budget/cache/PROFILE以及旧batches format不悄然改。新entry的费用/保留证明绑定实际新SHA及mode，不能把3ef旧通过改写成它已含fullview。

允许内部_restore返回新增projection槽或放decoder临时字段；二者选一个，避免两套decode/两次16c。若放decoder字段，drop必须在缓存/原native释放前清该临时view；成功只能由outcome保留，失败outcome=None。若返回四元组，outer新增projection/inner_batches等local必须逐名在finally清除，不能仅清原children/parse_usage/caps。

## 2. 精确插入与完整字段

原1051–1091先完成projection/source/defs/records/Catalog/payload/rows和逐字摘要门；1089 del safe_reason/safe_payload/encoded_payload，1090–1091释放safe4J scalar/2Jobjects。此时**raw、native、decoder.children仍可达**，不需要二次parse。

在1094–1099原A16 prepay及fixed metadata/scalar/object票通过后插入fullview分支：先留新增容器/标量块，后freeze；保持冻结结果到1103–1137所有原slot及一次原L16c结束，最后唯一返回。旧模式跳过freeze/新view票，保旧验收和费用语义。没有末child完成前的对外发布。

完整view由raw外层七字段和native reasoning构造，**reasoning值须取native，不取raw未恢复descriptor subtree**：

- outer7：format、implementation、reasoning、inputDigest、inputDigestDomain、sourceDigest、definitionsDigest。
- reasoning15：formatVersion、semanticsVersion、profile、rdfs、rules、warnings、evidence、rdfsEvidence、firingGroups、mechanismBatches、definitions、catalog、proofLeaves、termSources、graphBudget。
- child11：ruleId、definitionOrdinal、disabled、planDigest、batch、originalMatches、definitions、catalog、limits、budgetLimits、budgetUsage。

上述native child完整11字段在783–829已验证并保在dict中；不能从RestoredChild八字段或allocation补回planDigest/Usage。top raw implementation已过exact三字段和值核同，外层其余字段也是已核字符串。构造完整outer只复制固定引用，不重新生成摘要或前像。

## 3. 建议的冻结表示

用固定、exact frozen data record包已知dict，内部为immutable tuple of `(fixed_key, frozen_value)`或固定keys/values record；list转tuple。原list/tuple位置由fullview固定schema说明，不加会改变原值的自由tag。无需保存dict插入顺序作为wire含义；原数组、binding、false/true、head、basis、source出现及tuple顺序必须保。

只对已解码的exact dict/list/tuple递归；exact str/bytes/int/bool/None直接保留。固定canonical frozen records可作不可变叶复用：TermInput/SourceRecord/Variable/Triple/Comparison/RuleSpec/Catalog/BindingMatch/ComparisonEvidence/HeadEvidence/PreparedFiring/PreparedFiringBatch/ProfileValue/Number/Calendar/ProfileLimits。其嵌套成员已由decoder/发行/严格比较保证为tuple、上述record或scalar。特别ProfileValue.value不是任意object：它已被canonical parse并与保存str/bool/Number/Calendar全字段核同。

不要deepcopy/asdict重新构造PV；新副本没有canonical发行身份，或变成失去类型的dict。不要仅MappingProxyType(top)而保留内部budgetUsage dict或evidence list可修改；只读必须闭合到每个容器。不要用任意getattr/dataclass反射/动态import来冻结未知类；exact type身份比较先于foreign len/iter/hash/eq。

优先已知长度的预分配构建器，例如先留n+1 slots再建立 `[None]*n`、逐项写、最后tuple；同时预留临时list与最终tuple的峰值，转换后实际drop list。也可用iterator构造，但其length-hint/临时容量/引用搬移必须另给源，不能把tuple(generator)误说成只做n次最终引用写。

## 4. work、holding与原cap余量

### 4.1 walk与结构单位须分清

完整freeze是一次wire-backed树walk，访问的native container/key/leaf来源不超过payload中的原value/key出现，walk node数≤实际physical nodes≤B≤J。已验证immutable record作为叶，不再递归其全部字段；每次出现仍处理，不因alias跳费。没有新增第17次全树解析/序列化。

这不自动说明“所有结构工作只要J单位”。最终tuple/record、items临时pair、预分配清零/写引用、class dispatch、固定stack都需事前收费。建议每个container在取len后的创建/循环前按实际n/m预付构造固定量，child递归各付实际node量；完整构造工作保守目标≤16J，且记录实际新增量。16J是字段/引用单位上界，不是16次树遍。

**若root把授权‘freeze≤J遍历’解释为新增traversal-domain所有debit必须≤J，则不能仅拿本16J上界实施，应进一步证明具体构造式≤J或提交精确合同delta。** 按原阶段合同的“一遍节点walk+每节点固定结构单位”口径，它属于A16内部，不是额外未命名阶段。不应以文字解释默改最终授权。

可用于最终源码审的coarse余量分解（不是用cap大替代来源）：当前prepay阶段只有A7/8/10/11/12/13/14/15/16共9个，每次32J，实际已付288J。其余own-code操作可分别保守摊为：A1构建≤J、A2 native/collect≤4J、A3跨联≤8J、A4 PV结构≤8J（term_key固定24M另M域余量）、A5/6完整两边比对≤8J、A9重建与source比对≤16J、rows own refs≤4J，合49J；向上留64J。record dispatch由原recordType/tag/字段wire语法分摊；top Catalog/defs被N次比较的右侧以每child已保存左侧wire出现共同支付，没有无wire的N次free重复。固定context/17L/slots/receipt归N与常量，远小于65536N；key固定≤24M及PV固定call开销在64M内。

所以该表示若新增构造≤16J，新的coarse total≤368J+64M+4096N+4096，仍小于原512J+64M+65536N（N≥1）。这只是用于设计的固定算法source bound；实际constructor/dispatch/容器fee一旦不同，必须逐行重算，不准凭本上界倒填收费。

### 4.2 ordinary objects

freezer前一次性reserve新增`2J`对象/引用tickets；该块包括输出frozen containers及构建临时，实际分配前同时留票。safe树的2J已在1091释放，所以它们不并持。

固定native plain maps已有evidence(6)、rdfs_evidence(3)、leaf(2)、occurrence(4)、graph_budget(5)、child(11)、reasoning(15)，keys最短≥4字符；另有固定limits17、usage6、graph usage2、implementation3、outer7。每field的JSON key/colon/value字节足够摊fixed pair/record/引用；没有攻击者任意空map森林。array tuple引用按其原数组出现支付，canonical叶既有对象由对应recordType/字段wire开销支付。已发行PV的16个固定强引用/指纹/weakref相关metadata仍须在转交时映入保留块，不可因cache.clear把实际还由view持有的PV称已释放。

采用停止于canonical immutable leaf的算法时，递归容器层数由该固定schema限制（evidence→inputs→triple等），明显小于物理JSON35；建议实现固定≤8个容器frame且每frame≤12槽的显式stack，费用由A16 fixed块覆盖，避免未说明Python递归frame并持。构建器临时list+tuple和pair峰值仍在2J块。用别的表示/更大stack需重算，不能自动沿用2J。

旧AST≤J（每物理value/key至少2wire bytes，AST node+slot≤2physical），native ordinary≤J，structured references保守≤J；safe消失后新增view≤2J，coarse峰≤5J+16M+固定metadata。entry128N、setup128N、A16256N加其它固定record仍在2048N+4096来源内；因此无需扩8J+16M+2048N+4096 cap。future实际峰要核reserve顺序，不能拿default cap当已用量。

### 4.3 ordinary scalar与opaque

freeze不编码、不解码、不格式化或复制str/bytes/bigint。旧ordinary scalar票继续覆盖仍在raw/native/cache的载荷；额外建议reserve `4J`作为fullview长期保留块，避免依赖AST4token余量的隐式复用。完整view对应每个wire token的保留str按4B/codepoint、int/bytes载荷、固定发行数据可由该保守字节上界摊；返回rows原bytes另由raw票转交，不把rows重算。

该4J在freeze之前留，失败回滚；正常在新view仍活着时不得release。清临时raw/native/cache后，成功结果应明确转交这份view载荷的owner，随后operation cleanup置live0只是结束本次R持有，不能称对象已释放。

原scalar cap为16J+16S+16×65536M+1048576N+4096。将已知raw/UTF8/AST/native/safe/encoder/rows/key/fresh/context/receipt逐源保守叠加（故意含不同时阶段），旧峰上界30J+3S+65536M+526000N+32768；新4J后为34J+3S+65536M+526000N+32768。M固定131072，J≤25165824，S≥8388608，N≥1时cap差仍正128505579856逻辑bytes。这个代数差不等CPU/RSS或容量线，不跨域借票；source组成见静态JSON。若实现真复制scalar、重建typed payload或重复编码，必须另计而非直接沿此式。

freezer自己的固定容器构建不需要opaque；exact immutable leaf无需再canonical parse/16c。原每child唯一parse、16c、projection及encoder的opaque保持不变，完整peak仍由只读budget.opaque前置。不要新增with opaque后在退出时留一棵未转ordinary的fresh树；若确需库delegate，先交精确来源/持有delta。

## 5. receipt与真实转交/失败清理

A16现有256N+256objects、1024N+1024scalar/copy、128N+128traversal保留到receipt。新增result wrapper、projection根及inner batches临时应在新增2J/4J或该固定metadata块中各有归属；最终usage/peaks必须在所有收费/reserve之后取，之后仅构造已预留record、drop/cleanup/finish和return，不能在快照后再加freeze费用。

caller从唯一returned record获得fullview/旧batches/rows的实际强引用。返回合同应明确：caller在使用期间负责H/lease记账及最终drop；纯模块只给值/本次R使用量，不自签来源权或无限留存许可。本窗口不造H服务/Store/receipt。若需要重量data，可给保守估计，不能把它当H授权；至少包含view新4J/2J、原rows bytes、旧batches/expected implementation额外强引用和固定receipt。后续T01应在接收/移交前自己预留，并与R在过渡时双计。

共享entry新增locals建议预先None并finally清：projection/fullview、inner_batches、new wrapper/return_parts、冻结builder/stack（若挂decoder亦清字段）。失败outcome=None；成功仅outcome保留。先清分别持有native的locals与decoder临时view，再drop cache/parse pools，随后ledger.cleanup/finish。constructor、usage、peaks、freeze中途/尾项、view wrapper故障均须验证公开frame没有这些native局部或原异常context。若重构把操作移私有helper，原S2回归不能仅按旧函数名过滤而漏新helper frame；要检查所有持有过新增native的本模块公开异常路径。

## 6. 具体应防反例与未来验收

1. 新view只包旧RestoredChild：planDigest/budgetUsage等仍丢。必须7/15/11全部字段级签名。
2. 只tuple化top数组：nested child.budgetUsage或evidence.inputs仍可改。逐位置只读/类型/None/顺序测试，不能只看frozen外层。
3. 再调_ProfileProjection/JSON来freeze或deepcopy PV：额外完整walk、hex/scalar峰或发行身份都改变。保持原叶，测试view中的PV为该次canonical发行对象，旧checker实际一次。
4. reserve在constructor之后：将object/scalar下调到新增块差1时，freeze入口观察应为0次，失败live0/无partial；不要仅测事后cap≤usage。
5. freeze成功、最后slot失败或receipt/usage/peaks失败：新view即使完整，也不得从异常frame保留/发布前缀；保持累计work、不复用ledger。
6. native已drop后从raw再parse取rdfs：重复R_parse/树/费用且丢同一次生命周期。source/index/多head/false-tail原回归保留。
7. tuple(generator)只计最终n次写：长度hint/容量搬移或额外frame可能未支付。最终用已知len预分配或证明所选内部构造的保守块；单walk≠所有工作n。

实际验证须由root在新树独立环境运行，不由本审准备阶段执行。紧池包括每个新pre-reserve前门±1、freeze深/宽/末项、bytes/int/PV/source最后字段、全7/15/11 signature和原payload/rows不变、旧API确切类型/字段/错误、原实际producer一次与全slot原L API一次、公开frame清新locals。正常check/source与独立实际源码审仍必需。

本建议以固定e446及上述构造选择为限，存在实现选择和待逐行计数项；没有对尚未写出的新代码给通过。若最终实现无法满足所选≤J walk/≤2J对象及原cap/owner清理，先向根交精确反例/路径/最小delta，不扩大只读budget权限或降低完整字段。
