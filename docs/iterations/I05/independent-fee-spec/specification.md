# I05 独立逐 occurrence 收费规范候选 V1

本候选由第二位全新上下文作者独立形成。结论：现行资料能精确复算分池、若干字节编码和数学关系，不能唯一决定完整五 operation 的费用或 114 个调用的首个耗尽点。下面把可证合同与最小新增收费提案分开；`i05-fee-events/1-proposal` 尚待接收，绝不声称 6891 或任何产品已遵守。本窗没有调用产品、图算法、比较器、旧测试、probe、generator 或历史 actual。首作者隔离事故原件只作 bytes/hash 保全，未读取其内容。

## 1. 来源、等级与符号

完整固定 ref/path/bytes/SHA 在 review 的 `input-manifest.json`；逐条原行及片段 hash 在 `normative-claims.json`。以下简称 Q=9333 的 q6 文档，I=de37 的 integration，R=851e 的 restore，P=a359 的 producer，D=6891 的 direct 合同。文档中的“拟/建议/申请”继续标为提案；采用表只能证明选择性采用范围，不将这些措辞提升为已实现。允许的 2d5 片段是后实施局部证明，只支持 64 控制对象和 4M 摘要覆盖，不支持完整先验 invoice。851e cache 是局部数学证明，不是全部 R≤原 W/I。

| 已有命题                                                                          | 等级                                     | 能推出 / 不能推出                                                                                                   |
| --------------------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| I:63–80；R:101–109：sorted rule_id、七总池、disabled/dummy、compile/eval 同 child | exact 分配规则                           | 可预测所有 17L 数值；不能制造原 allocation/capture/issuer                                                           |
| Q:58–67：字节扫描、每定义/绑定/比较/head/trace 至少1、32bit limb                  | exact 单位和若干算式 / 下界              | mul=L(a)L(b)、每 division/GCD 步积精确；项数“至少1”不是 exact 1；未固定 parser/encoder 的全部步数                   |
| I:80：图 work≤1M、triples≤100000；Q:58–65 机制硬门                                | cap                                      | cap 是最大准入约束，不是 usage，也不保证所有小图成功                                                                |
| R:93–99：49B framing、完整键、逐 occurrence 核值                                  | exact 编码 / 行为关系                    | key bytes 可算；cache hit 不免 wire/key/核值费；旧 alias/issuer 不可由 JSON 恢复                                    |
| R:117–184：R 多域上界、A1…A16                                                     | 保守上界与拟算法合同                     | ≤cap 未必是 exact；必须有实际逐 loop 映射后才适用                                                                   |
| R:188–194：R_parse 子集、16c 三池                                                 | 条件上界 / cap 精确公式                  | 同版完整原成功及可信 L 前提下成立，不能替代发行身份与原 matcher 完备性                                              |
| P:149–157：C/T/S/H、八 stage、聚合                                                | 拟上界                                   | 不把大系数当逐项 exact；不增加第九 stage 或原 cap                                                                   |
| D:117–155：全部候选、首插入、trie、DP、whole-J                                    | exact 固定部分 / 其余实际计费 / 分析上界 | A≠S；8A+32S+16K 只是traversal部分项（独立2K扫描同时进work，除非有包含关系证明）；全输入/重复流/receipt/cleanup 另费 |

符号避免旧文件重名混淆：`B`=payload+rows 原 canonical bytes≤8MiB；`Qp`=input/source 前像合≤16MiB；`Jnode`=wire 的 value+key 节点，R 中≤B+Qp；`Jflow`=某次完整序列化/传输实际字节，绝不是节点数；`Kocc`=所有完整键编码字节累计（含重复）；`Acan`=closure 实际候选 occurrence，`Sstep`=首次插入 steps。`Fcap_i/Ocap_i` 是限额，`Fused_i/Oused_i` 是真实用量；16c K 公式使用前者，不能换成实测量。所有量为非负 exact int，bool 不作 int。

数学函数 `L(z)=max(1,ceil(bit_length(abs(z))/32))`。字节长度一律 UTF8，不用 codepoint/pretty JSON 长度替代。source 依 reference/digest/revision/text 顺序保 None 与空串；language_raw、lexical、原 ordinal 不归一化。RDF identity、值相等、完整键相等、Python alias、授权身份是五种关系。

## 2. 17L、七池和权威分离

固定总池依次 work=16777216、input_bytes=262144、output_bytes=262144、trace_items=8192、firings=1024、head_occurrences=16384、bindings=1024。其余十项保持：term_bytes16384/source_bytes65536/digits4096/integer_bits16384/temporary_bits32768/rules100/when16/comparisons32/heads16/variables64。完整 17 项名字、值见 `fee-contract.json`，不从外来保存字段反射。

先核 exact 定义、唯一非空完整 rule_id、UTF8≤16384，再按 Unicode codepoint 排序（无 locale、无 Unicode 规范化）。定义数 n=0 时 N=1，唯一 dummy 的 id/ordinal=None；n>0 时 N=n≤100，保原 ordinal。每池 T、排序槽 j：`a(T,N,j)=floor(T/N)+[j<T mod N]`。disabled 照占槽且完整 compile；不 evaluate、originalMatches/batch 保 None。dummy compile 空定义、核 Catalog、evaluate 空 matches、保真实空 batch。enabled 零匹配同样有空 batch。七池各 Σa=T，结构上限不乘 N；余额不回流。原 ordinal 不发余数。同 child compile/evaluate 只用一个原 Budget；不能后阶段重开、每 head 开池或借别 child。

独立预测 L、已知数学结果、提案 invoice、实际 capture 四列分别存：`predictedAllocation` / `mathFacts` / `proposalInvoice` / `authority`。最后一列含同次真实17L、planDigest、budgetUsage、原 child/source/matcher/producer 发点与 T01 授权；未知用 null+missingReasons，不填0、空 batch、假 issuer。正确预测 17L 不是已取得 OriginalAllocation。数学/结构结果可 exact，资源准入仍 pending。

16c 每原 child 一次，同原 L：work cap `3W_i+k_i`，input `2I_i`，output `2O_i`；`k_i=203+33Fcap_i+4Ocap_i`。整次 `Σk=203N+33×1024+4×262144`，不是每 child 领完整默认。R_parse 独立每 child 原 W/I、output0；只有不同完整 PV term key miss parse 一次。同版原成功下 R_parse≤原生产 parse 子集；cache 每 hit 仍付完整字段/key/核值。没有成功前像/原 capture 时该蕴含不可用。

## 3. 最小新规范：可计算 event 账，而非反推实现

以下全为 **proposal**。它填“至少1”和遗漏事件的精确规则；原值域/数学/first-witness/语义版本、旧 cap、错误分类不变。引入独立成本版本，owner 接收后逐项实现或保留 pending；不能用本 proposal 解释旧 actual 或把不匹配视作旧产品已错。现行不可改委托仍按原批准 block 预付并在原域记账，新事件只解释该 block 的覆盖义务，**不再重复扣原 exact 固定票**。若不能证明映射在旧 cap 内，应优化/重新设计，不能升 cap。

账本按 `(operation, actor, artifactOrdinal, childOrdinal, domain)` 分域；operation 恰 profile/fullview/dag/restore-negative/roots。C0/R0/Dc/Dr/roots/graph/M/R_parse/16c/T/S/H 独立，单位不相加为物理标量。事件是外部规范的数学对象，不是要求产品每步分配日志。模型只对独立手列事件及长度/整数收费，既不产生图/matches/PV，也不编译业务 fixture。

| 原子事件                    | exact 提案收费；均在访问/分配前                                                                              | 计数和排序                                                                                                                       |
| --------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| ITEM(kind,n)                | 所属 work +=n；n 个定义/字段/tuple-slot/候选边/索引访问/绑定扩展/比较/head/proof/trace；每个 occurrence 一票 | 原数组位置或已固定排序；重复/失败候选不省                                                                                        |
| INPUT(n) / OUTPUT(n)        | work +=n，机制 input_bytes/output_bytes +=n                                                                  | 每次机制编码的完整实际 bytes，不是 unique source bytes                                                                           |
| SCAN(n)/COPY(n)             | work +=n 且 scan_copy +=n                                                                                    | UTF8/词法/转义/十六进制/构造 key/完整串比对，读或写每一遍分别一事件；两边字符串比较预付 len(left)+len(right)，即使首字节不同不退 |
| HASH(n)                     | hash_bytes +=n；机制域另 work +=n                                                                            | SHA 读取完整 domain+preimage。typed digest / payload / rows / source / definitions / Catalog / receipt 分列，不能一个摘要抵其它  |
| ADD/SUB/CMP(a,b)            | work +=max(L(a),L(b))                                                                                        | 每次符号/大小比较、加减各一事件；不按结果相等免费                                                                                |
| MUL(a,b) / DIVSTEP(a,b)     | work +=L(a)L(b)                                                                                              | division/remainder/GCD 的每个 Euclid 步分别预付；不把 gcd 当一票                                                                 |
| SHIFT(a,k,outBoundBits)     | work +=L(a)+max(1,ceil(outBoundBits/32))                                                                     | 运算前独立证明输出 bit bound；先核 temporary_bits，再做运算                                                                      |
| HOLD(handle,objects,scalar) | reserve 实际逻辑引用/slot与 byte/limb tickets；峰为所有未 RELEASE 之和                                       | unique handle；alias借引用也有 slot，底层 owner 的对象/bytes只计一次但不能无 owner                                               |
| RELEASE(handle)             | 只降低 live，不退 work/scan/hash；drop 引用及 slots 另 ITEM；成功转移先向接收 owner HOLD 再释放旧票          | 不因 ledger.cleanup/live0 推断 GC/OS RSS、pipe终止                                                                               |
| BLOCK(name,vector,live)     | 完整命名不可改委托按已批准静态 block exact 预付；返回成功结果转 ordinary HOLD，失败使用预付清理              | 未知委托无 vector 就 pending，不默设0；不得伪造内部 hook                                                                         |

所有累计域有独立 cap；向量预付检查先按合同固定域序（work,input_bytes,output_bytes,trace_items,firings,head_occurrences,bindings,scan_copy,hash_bytes,objects,scalar）核全，全部足够才一次扣，访问随后发生。一次向量有两个不足时首域稳定。失败 attemptedDebit 与此前 paid 保留；本次未执行动作不收费，过去不退款。预付控制票包含有限计数更新/固定状态及其固定生命周期清理；bootstrap64是固定控制表示的逻辑reserve，不是可反复消费的64个data slot。finalization的handles/slots只列新增data，固定控制清理包含在其固定字段/状态处理，不遍历外来数据。普通；每个 ITEM 的1亦包含一次计数更新，不再为其递归制造 ITEM。计费日志不是免费第二棵树：完整逐事件 audit 如需生产保存，其分配/编码归 C/T/H 的独立受界载体；本窗纯数学模型在产品外保存。

开户 new→running 后不得 begin/retry；C 固定64 object bootstrap、D 固定128控制票按各原合同，不向 cap 增64/128。普通事件执行前另预付一个有限 finalization BLOCK：固定 receipt字段/计数快照、摘要domain、cleanup 最大 handles/slots 的 work 与保留空间；receipt内容不含自己 hash，先编码 receipt_body 再 hash；包裹 hash 的外层另编码一次并付费，禁止自哈希循环。最终只转移已 HOLD 的 receipt/result。失败分支以已预付块清引用、只给受限诊断；容量不足以预付 finalization 时不开数据容器。本 proposal 不把 cleanup 新开无界 emergency 钱包。实际 receipt 大小/handle cap 必须在每 operation 前置表给出，否则该条 pending。

## 4. 逐 operation 最小 delta 与完整顺序

下表是必需的具体事件位置；详表 `operation-schedule.md` 给每一个未规定的子动作、所有分支与持有。任何子动作没有独立数学长度或实际发点，就不能发布 exact invoice。

| operation        | 固定顺序、必需分账                                                                                                                                                | 接收前置/禁止的简化                                                                                                |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| profile          | counts/bytes/shape → 原定义全 compile → graph build/index/sort/closure/match → 每 child全部比较、all-true全heads → 全批typed编码/投影/rows/hash → receipt/cleanup | 图与机制分账；false后比较照执行；后项首错不返前缀；所有 source/Catalog重复付                                       |
| fullview         | prepare C0 → 单次真实 producer +旧 graph/M → C0 projection/copy/hash → 原同次wire → 每次独立R0+R_parse+16c → freeze完整7/15/11 → receipt/cleanup                  | 无D；全部17L/usage保原值；不是只核children；Turtle独立原前像                                                       |
| dag              | fullview相同基础 + Dc所有候选/首插入/link/编码 → Dr全steps/coverage/DP +R0 → 仅成功且targets非空时roots                                                           | 新7/16/11与finite8/schema2精确分派；structured-only；原 Acan、步骤、重复key与全流并持                              |
| restore-negative | 先证明真实生产准入及完整成功；保存原expected/L；只改 receiver bytes → 版本/原wire摘要/strict schema…顺序失败 → cleanup                                            | 不能rebind摘要使后尾篡改越过原摘要门；资源先耗尽可先于非法；失败绝不roots；未成功生产则 receiver阶段未执行         |
| roots            | 全恢复成功view +实际targets → 每target原顺序核key/查索引 → 返回全部leaf/step/每firing/head occurrence引用 → receipt/cleanup                                       | 无target按调用合同不调用；直接显式空targets调用收费entry/receipt但返回空；重复target逐次付并保返回分组，不去重请求 |

稳定性：保持已有图候选 `(result key,ordered premise keys)` 稳定排序和首插入，不加rule/depth tie-break、不找最短。已有文字没有完全规定所有 index/sort/scan 的 exact 事件序，新增收费不擅改其语义顺序。owner 须供应**纯规范动作清单**或批准独立 charge traversal（只计费不重reason）才能把每 ID 的图账从 pending 变 exact；不能借本模型模拟当前 matcher。成本排序采用独立、版本化的有界 stable insertion schedule：每原数组 next item 向前比较直到≤位置，完整byte比较收费，移动slot另ITEM/COPY；若批准采用该 charge schedule，它只规定费用，不替换首次witness排序语义。实现用其它sort须证明同 exact 费用关系或版本化delta；不能引用 Python sort 平均复杂度倒算。

## 5. Typed、序列化与摘要的精确 delta

typed数学不换语义。数值 Horner/约分/舍入等每个 limb 操作的步序现行未完全冻结：提案要求提交独立 `ArithmeticWitness`，记录每次输入的bit_length、输出先验bound、mul/div/gcd/shift/add序号及数学关系；从纯值推导，不从实际usage抄常数。十进制按左至右每digit `v←10v+d`，每digit分别 MUL 与 ADD（含0）；指数 bounded square-and-multiply按指数binary从MSB，先核digit/bit门；GCD按非负Euclid余数至b=0，每个非零b的DIVSTEP都列。binary32/64只一次目标格式round-to-nearest-ties-even：商余分离，每次移位/除余/比较/进位逐项收费，负零保留。Calendar day/second保持分开；年转换400年周期的商余与日期组件逐次列，不把宿主datetime当免费。语言/IRI/boolean/regex/UTF8必须供应有限DFA或BLOCK的最坏计费证明；未供应就 pending，不自定Q6答案。该 witness 是数学证明载体，不是可冒充PV的对象。

常量只在compile parse；binding每真实使用事件、每comparison双operand的身份/值核验与编码仍分别付，不能因常量已解析就省遍历/typed fingerprint。全部 RuleSpec/Catalog字段按原顺序；重复 Catalog每 child compile收费；保存 top与每child副本每出现读/核/保留。typed输出payload与JSON wire不同编码域，前者精确字节规范当前不足，`typedByteExact=null` 直到T05供应独立字节合同，不把独立JSON长度冒充typed encoder长度。

本 proposal 的 **外部 invoice/planDigest 前像**使用独立明确 binary TLV（仅规范载体，不替代现行planDigest）：header ASCII `I05FEE1\0`；None=`N`，bool=`T/F`，int=`I`+4B长度+ASCII canonical lowercase hex，str=`S`+4B UTF8长度+bytes，bytes=`B`+4B长度+bytes，tuple=`A`+4B项数+逐项TLV，record=`R`+4B字段数+按本schema给定顺序的(fieldName str,value)。最大uint32 framing；超长先拒不截断。域前缀为ASCII `I05-FEE-PLAN/1\0`，preimage为定义、Catalog、ordered rule_id/ordinal/disabled、17L、cost-version/source-manifest-hash的完整record，不含producer身份断言；SHA256只作新字段 `proposalPlanDigest`。现行 `planDigest`字节公式未获独立规范，继续保值/绑定原payload，不重命名或倒填。整数hex/UTF8/TLV可由独立模型计算；不解码业务archive。

JSON需按各现行明确codec的 canonical规则，若完整escape/key排序/typed tags仍无独立说明，不猜输出；不能因为Python json能encode就称它是产品canonical。独立 invoice JSON本身固定UTF8、sort_keys=True、ensure_ascii=False、separators(',',':')、禁止float/NaN/surrogate；其bytes只属于本规范。对所有原whole-J重新序列化/hash/copy按完整实际流收费；ΔD不是旧C0/R0全流费用。N3格式化保守预付字段UTF8最坏4倍、转义6倍+32，实际重复K门累计；原允许representative与source occurrence分别保留。

## 6. 可判定性与验收

`per-id.json` 全82+32保留原ID/datasetPointer/projection SHA和每项独立状态。每项分别给：纯输入结构计数 exact；独立sorted allocator全部17值 exact-prediction；整数比较数学 exact（有值的18格）；其他图/多head语义只保既有手选expected关系及其未审来源，不能冒称本窗已独立枚举；完整现行费用为 [可证下界,未证上界]、pending exact；原authority独立missing；条件错误谓词精确。失败oracle不能接受任意RESOURCE_LIMIT。

判定规则：若完整独立invoice+真实cap+发点映射齐备，所有prefix预付≤cap且语义无错，则预期success，任一RESOURCE_LIMIT为误拒；第一次独立所需向量超过cap，预期该精确stage/domain的resource拒绝，别阶段/别域为不符；语义错误先到则仅该首错成立。仅有下界L且L>cap可证资源不可成功，但未固定prefix次序不能捏造首域；有可信上界U≤cap并证明所有子域/hold均受界时可证该操作资源足够。L≤cap<U或缺U/发点时 pending，不能把资源拒绝和成功都标Pass。source/package一致只是一项关系，不能替独立oracle。

全部小账在 `hand-examples.md`：预先字面手算期望独立于模型，含成功、差1、零余额、false后首错、重复比较/全heads、disabled/dummy、alias/cache、重复restore/roots、临时并持、receipt/cleanup。模型只验证这些数学事件；不运行产品、不证明417 oracle、正式Job/预算已过。后继与实施delta在 `handoff.md`。原Goal/六迭代/57、SQLite HOLD/whole-H/owner、正式Job、指定同版双审/CI/两OS/真人/develop门均保留。

新增唯一纯接口参考：root另授的api-defaults-reference.json仅声明6891 execute_profile/execute_profile_records的rules=()/disabled_rule_ids=()默认。Turtle行可精确列“若真实调用canonical API并省略参数，则dummy17L”的条件值，不能从API默认推断fullview producer的接收调用约定或真实原capture。故113项无条件预测+1项条件默认预测，当前调用绑定仍pending。

proposalPlanDigest 的严格字段序为 `definitions,catalog,allocation,cost_version,source_manifest_sha256`；Record无额外字段。definitions为原ordered RuleSpec tuple，RuleSpec字段序 `rule_id,when,comparisons,heads,source,revision,definition_digest,policy`；Triple依 `subject,predicate,object`，Comparison依 `left,operator,right`，Variable仅name，TermInput依 `kind,lexical_form,datatype_iri,language_raw,source`，SourceRecord依 `reference,digest,revision,text`，Catalog依 `classes,object_properties,data_properties`。allocation为sorted slot tuple，每slot依 `rule_id,definition_ordinal,disabled,limits`；limits依fee-contract.json的fields17顺序。所有机制序列都用TLV tuple，record类型由这些位置与exact字段集决定。原undefined非None字段不得靠省略重建；未知前像则proposalPlanDigest pending。最终哈希字节为 `ASCII("I05-FEE-PLAN/1\0") || ASCII("I05FEE1\0") || TLV(rootRecord)`，不包含digest自身或任何issuer自述。模型的Record/TLV只编码这些独立规范值，不发行业务类。
