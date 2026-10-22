# I05 独立逐 occurrence 收费规范 R2（仅提案）

本版补齐 R1 F1–F3：固定 82+32 项各有完整、确定、可重算的收费程序和非空分池金额；baseline 有完整输入字节、2282 个逐 prefix、独立手算及782字节 receipt。它没有给现行产品补造 invoice、usage、issuer、Job 或成功对象。R1 的报告、旧表、旧 manifest 与失败记录保留，入口改为本版。

## 1. 已知合同与提案的边界

现行独立输入及16组原行证据仍见 review/input-manifest.json、normative-claims.json。固定七总池是 work16777216、input/output各262144、trace8192、firings1024、heads16384、bindings1024；十结构项 term16384/source65536/digits4096/integer_bits16384/temporary_bits32768/rules100/when16/comparisons32/heads16/variables64。sorted完整rule_id后逐池divmod、余数给前child，disabled照分，原ordinal不获余数；compile/evaluate同child对象、不回流、N0独立dummy。这些值能精确预测，不是同次原17L的发行证明。现行“至少1”仍是下界，不能倒填任何 exact。

G 保持 MAX_TRIPLES100000、work1000000；D 保持 A250000/S100000/K与carrier各8MiB、work/scan各581671040、objects270635588/scalar50331776；payload+rows仍联合8MiB。C0仍按原 A=Q+D+8MiB+16MiB、N计算；R0保原 B/Q/J/M/U/S/N上界；16c保持3W+k、2I、2O。新程序没有提高任何这些cap。全局 H 必须由真实 T01 owner另核真实额度；wholeOwnerHRequiredPeak是本提案逻辑并持需求，不是RSS、Q5、512MiB或真实quota。ENTRY/M/Rp/R16的巨大有界数学arena guard仅防纯解释器无限计数，并非新增产品容量/owner授权。

现行 codec、planDigest/fingerprint 的实际编码、真实 producer/原allocation/同次usage/原wire/expected/source权限仍 C 类 pending；每ID保留该栏。这里定义**新 namespace 的编码与 action schedule**，使新提案本身不依赖未知实际量。`amount`是完整数学程序需求；`paidPrefix`只到精确首拒之前；后续事件标 analytic-unexecuted-tail，绝不称失败后继续执行或成功前缀。现行准入/首错仍须现行完整独立发点证明，不能用提案首拒替代。

## 2. 许可、输入与 proposal binder

A/B/D窄授权和最初请求的原字节见 review/r2-provenance：6146B/SHA14af3479…授权独立 binder、数学图/绑定仅为枚举收费、全114解释器；10144B/SHA0223baba…仍是原请求历史，不回写为全部获批。后来明确批准的Q6纯规范固定为9333e69234a6f54a0dfc1485f49d8fdeb4b69cfd:docs/iterations/T05/q6-adopted-profile-v1.md，16428B/SHA9259f4ac…；副本是`.raw`。不读产品算法、现行probe/tests/generator、actual、首作者草稿或投影WIP。

固定 inputs.json/oracle.json/gaps.json 的 bytes/SHA 在 run_reference.py 逐件先核；数据源分别是0e42a0fe349054a92817cb4d463bccdc15f6c042和3d8f4ee912f41bd03388322d29a9bfc0e7defe85。oracle只消费允许的独立业务数学，未读取运行结果。输入/外部手选数学可独立消费；pending authority不遮蔽其值。

Binder在 reference.py:bind，输出只叫`proposal-only-fee-material/2`。

| 字段                 | 确定映射                                                                                                                     | 来源状态与禁止误认                                                                                            |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| profile records      | asserted后ontology，原顺序每row三TermInput；raw N3常量用独立JSON字串/后缀解码，变量另Variable                                | 原row已supplied，结构化私有字段原先omitted，映射标proposal-synthesized；不声称原产品已用这些字段              |
| typed records        | 精确五字段及完整SourceRecord原值                                                                                             | supplied / explicit-None / explicit-empty逐field保留；None、空串、source缺失/存在分开                         |
| profile SourceRecord | text=该完整原row的独立canonical JSON；reference=固定input ref+真实dataset pointer；digest=SHA(text UTF8)，revision=input ref | **新提案来源记录**；raw source locator仅为被引用row的一部分，绝不直接当SourceRecord或生产许可                 |
| typed SourceRecord   | reference/digest/revision/text四原字段逐项保留                                                                               | 其文本不是由term反推；不认证actor/job，不能以digest代权限                                                     |
| definitions          | 原顺序/原rule_id、when/comparison/head位置；原revision/digest能供则保；profile常量来源指完整定义row                          | 衍生typed结构与缺policy=固定已采用profile均明确proposal-synthesized；没有猜字节span                           |
| disabled             | 原supplied列表，包括显式空；缺项仅新提案调用选择空                                                                           | Turtle缺rules/disabled的API默认只标API-default-conditional；新提案显式选择空调用，不证明原observation如何调用 |
| Catalog              | 只收原record中rdf:type到owl/rdfs Class、ObjectProperty、DatatypeProperty的声明；排序/去重本身收费                            | 头结论不补真实许可；没有从heads偷偷添加类/属性；重复声明逐次扫描/查索引                                       |
| Turtle               | 原text整串仍是字节/source前像；固定独立inputGraph仅为数学parse witness                                                       | 不生成/反推原Turtle，不伪造新生产解析结果；全原text字节仍逐次读/预付                                          |
| mode/preimages       | 参数给则supplied；未给是新提案显式 records/text选择；records/source/defs分别canonical JSON                                   | 每个preimage长度/SHA在binderMeasures；不是当前native编码或当前expected原前像                                  |

fieldOrigins按每个字段和嵌套SourceRecord展开，含inputState和valueOrigin；程序配方给实际observations数组pointer、独立数学pointer、参数和输入SHA。raw字串里不存在的私有字段标omitted并绑定其真实raw容器；未把synthesized值标为真实发行。全114的这些字段在all114-fee-programs-r2.json，不能由表的一句pending替代。

## 3. 精确新 fee-codec 与数学值

新fee-codec是独立二进制格式，不能作为产品wire/planDigest：N=None，T/F=bool；I+u32BE字节长度+canonical `hex(int)` ASCII；S+u32BE+UTF8；B+u32BE+原bytes；A+u32BE item数+按序items；R+u32BE pair数+按**构造schema顺序**key/value编码。bool先于int分派，不接任意对象/回调。None与空串不同；列表/tuple同A；所有整数先查固定位/长度，再有界编码。`shape`递归计每value及dict key各一object，array每槽、dict每pair两槽；H的logical slots=objects+slots，scalar票按完整编码字节计算。数学arena是固定预付上界，不能当Python heap测量。

独立小字节例与字面golden在test_reference.py：None=`4e`，é=`5300000002c3a9`，-1=`49000000042d307831`，`[true,null]`=`4100000002544e`。完整baseline输入 native85953B的hex原件、保持schema顺序的JSON副本均保存；独立第二编码器核其字节SHA。**输出只在内存中构造以计费**，不导出新业务expected/图/业务payload供产品；新输出长度/SHA和完整编码程序可重算，不能拿这些SHA喂T05。

提案数学值固定四字段term/domain/value/language；term含完整raw/source。N保精确numerator/denominator及仅binary浮点的negative_zero；S/L/I/B保实际值；Calendar保独立day与有理second。fingerprint完整preimage=`I05-FEE-VALUE/2\0`+encode(value)，比较复核另`I05-FEE-CHECK/2\0`；plan另`I05-FEE-PLAN/2\0`，batch另`I05-FEE-BATCH/2\0`。完整source和重复term每次编码，不按值eq免票。leaf ID只在C0发行数学引用时对完整RDF key哈希一次；D link只借该数学引用，不第二次伪造producer hash。

canonical JSON仅新fee projection：ensure_ascii=false、sort_keys=true、compact separators、allow_nan=false；int投影为integerHex，bytes投影为lowercase hex二字段，原顺序array保留。rows按原JSON字符串每8192 Unicode字符切一行、UTF8重新编码；payload与rows分别全摘要、联合计B并用WIRE8M门，不混机制output池。原现行recordType/schema codec仍pending。

## 4. Primitive与先付规则

所有primitive先获得其完整向量和已预付workspace，然后动作。扫描/复制同时work与scan_copy；hash同时work与hash_bytes；INPUT是完整编码字节+全部value/key节点的work、完整字节input；OUTPUT为完整batch编码字节进work/output。ITEM(n)=n work，不按unique content去重。计数更新有固定有限primitive，不递归自生收费事件。

| primitive                         | 新提案精确收费/顺序                                                                                                                                                                                   |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| whole bytes / encode / comparison | SCAN(n)=(work n,scan n)，HASH(n)=(work n,hash n)；稳定insertion排序先付每key完整编码、每比较两侧完整字节及每移动/插入槽                                                                               |
| lookup                            | 独立byte-trie：完整key SCAN(K)，再ITEM(8K+1)；原结构化key、重复查询/未命中同费                                                                                                                        |
| limb                              | L(x)=max(1,ceil(bit_length(abs x)/32))；add/cmp=max(L)，mul/div=L(a)L(b)；临时输出bit上界先≤32768，再HOLD/扣work，再算；持续值≤16384                                                                  |
| shift                             | 先独立证明输出bit上界，再ITEM(L(input)+L(output bound))，不可先shift再检查                                                                                                                            |
| decimal/integer                   | 完整ASCII词法；每digit Horner mul10+add digit；显式指数零的两primitive；10幂从1按binary square/mul；Euclid每非零除数一次div，再两次归约div；每步先bit/票                                              |
| IEEE                              | 已采用六numeric，不经过宿主float/Decimal；指数先文本扫描比较，远D界32:≥50/≤-61、64:≥400/≤-401；全零直接有符号零；近界按精确比值修e、divmod、2r比较、ties-even、再核溢出及归约；合法远下溢不能全部拒绝 |
| calendar                          | 按Q6YEAR、Gregorian floor/mod公式；0000/-0000同天文年0、-0001为-1；完整有理秒、合法24点进日、显式offset归约，保day/second分离，不把巨大year乘fraction分母                                             |
| strings / language                | S采用XML1.1 Char*；L scalar不额外套XML限制；完整ASCII RFC5646 ABNF、grandfathered全集，允许ABNF未排除的重复variant/singleton；128×tag bytes固定有限状态检查票，非registry-valid                       |
| IRI/boolean                       | IRI仅已有入口precondition下的scheme/禁字最小检查票8×UTF8 bytes，不声称完整RFC3987 parser；bool仅四种原词法                                                                                            |

九域N/S/L[t]/I/B/Dz/Dl/Tz/Tl：只有同域、同L标签可比；N六类型混型全部六算子精确；I/B只有eq/ne，其余整任务type error；不同域即使ne也报错。先合法词法/有限/预算，再矩阵，不把非法/NaN当false。SHACL finiteUTC/整数data-policy完全不变，不因Q6通用日历允许year0、无TZ或24点而宽化旧消费者。

## 5. 完整动作程序和所有分支

可执行规范是reference.py（stdlib纯数学）及固定输入配方；不是产品算法副本。局部数学图/绑定只决定收费枚举，并与既有纯数学的完整RDFS/custom集合、有声明的ordered witness逐项核对。不把新graph/batch输出到业务expected。每ID sourceSha、programSha、eventCount与金额都固定；任何ID可用run_reference.py --events ID在本数学目录生成完整prefix。调用不需owner后供任何费用变量。

E01–E09依次：bootstrap64/control、receipt与全生命期静态预付、原raw JSON全部读、三前像分别编码/复制/摘要、binder字段/SourceRecord生成与完整复核、Catalog全部重复声明及17L allocator、所有raw term/source occurrence输入解析。每child先完整compile，之后才graph closure与match，disabled也compile但无eval，dummy完整空compile/eval。source/raw/J没有未知补0。

G01–G09：seed每occurrence查key及首次插入；完整稳定排序；每round重建predicate index；type×subclass、subclass×subclass、domain×current、range×current全部pair（literal range不产IRI subject）逐访问/全term比较；每成功candidate原G4，A包含最终重复/落选；全部candidate稳定排序及存在性查询；首插入的完整premise leaf输入/union/输出/排序；至固定点；每when原位置对每partial binding×完整有限graph访问，重复变量全term比较及全部partial slot。保28与84等原occurrence，不按去重后图替source/费用。

M01–M04：完整定义/Catalog/17L编码、结构/变量闭合/所有常量/受控heads预检；给定binding完整when/proof/source、稳定变量/leaf序；全部comparison左右operand/fullfingerprint/域/六算子逐个执行，false不跳后项；alltrue后全部heads原index逐个RDF位置/完整Catalog检查；每个basis输入叶查索引并完整排序；全batch包括重复head出现、facts按RDF key去重后完整编码及独立摘要。末项语义错不发布前项；资源错原子拒整向量、既往扣费不退。

C02–C04：数学native view、projected tree、全payload/rows缓冲同时HOLD；全field/节点/slot访问、全stream三遍收费；payload/rows/source/definitions/Catalog摘要分列。WIRE8M计完整联合bytes，不能用机制OUTPUT或payload单项替代。投影树完成后释放，原native与wire在接收期间并持。

D01–D08：每D池128控制，原cap内；捕获开始前即预留静态完整arena；所有A的8费、实际S的32费、全部seed/result/premise key的18K（16traversal+2 scan同时进work）、旧leaf-ID link的key/引用扫描、完整carrier两遍；K/carrier各8MiB。A/S/E/K/B都在directMeasures给出。Dr核每有序premise kind/ref/ordinal、全部step字段/bytes/depth/template、实际每premise叶输入及union输出，逐输入trie查/逐输出key复制；不把2×输出数当实际输入数。

R01–R17：每次接收独立钱包，原B/Q/J/M/U/S/N bounds不提高；原wire UTF8/完整hash/与held payload字节全等；负例只篡改数学receiver对应enum，original held不动，通常先完整字节门拒，不假装到末field。正例原view/新view/原wire/前像/opaque parse空间并持；A1–A16每行完整J tree/key/slot预付32J及4(B+Q)复制，A1/2/11/12另全wire。A2固定schema表候选4096J和有界8位hex decode/shift/reencode票；A4按每child完整49B-framed key，hit也付两次全key、257(K+1)有限query票、32B separator hash、全saved/fresh字段比较；miss另split512/index704及完整独立Rp parse，强ref保到本次接收结束。top/child两处savedPV均逐occurrence，不把cache命中/alias免费。

A14各原stream/顶Catalog摘要分列；每child R16按原新提案17L、3W+k/2I/2O池完整重新compile/eval，saved typed bytes再编码/摘要一次，disabled definition-only、dummy空batch各不同。全返回数学layout的所有7外键/15reasoning键/11child键（D加directSteps）均受完整J检查/byte-equality；此layout是新fee namespace，不能冒现行codec已冻结。所有委托ticket价格为精确**预付上界票**，不是事后实测usage；每张票动作/数量已由新输入计算，不是未知BLOCK或caller后供金额。

Q01–Q03：只在实际新提案调用约定请求roots后，先HOLD整view借用；每target原序（重复照做）完整key查询、全leaf/step/每firing/head occurrence比较，全部引用保分组；完整返回buffer的编码/发布费用，原view pin到输出生命期。无target按本固定观察约定不调用；显式空调用的entry/receipt仍见独立手列程序，不把它当默认未调用。

这些规范包含错误分支：结构/计数→原定义闭合/常量/heads预检→binding完整→全部comparison原序→alltrue全heads→完整输出；预算向量先拒可覆盖未扫到语义错误。未执行尾段、最后child坏无成功前缀、disabled、dummy、hit/miss、无root、重复root、负wire均明确。模型对固定114均能完成其数学程序；另行手列非法/最后项错误程序在state machine上验证首错/清引用，不能用当前产品的Fail来校准本方案。

## 6. 五operation的 receipt、retention与terminal

| operation        | 完整责任                                               | 终态成功保留                                | 必须并持/释放                                                                                                                      |
| ---------------- | ------------------------------------------------------ | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| profile          | E+G+全部M+C+H01                                        | receipt与完整native fee-result票            | material、编译/数学graph/bindings/typed batch workspace、native、projected、payload/rows overlap；projected先释放，其余临时H01释放 |
| fullview         | profile全部+独立R全部child与16c+H01                    | receipt与完整restored-view票                | 原producer native/wire/前像、接收raw/schema/cache/fresh/native、opaque parse、复核batch同时计；receiver全过才原子转移              |
| dag              | fullview全部+Dc/Dr及被请求roots+H01                    | receipt、restored-view、若有roots返回buffer | seed/tempStep/index/carrier/DP/full-J全部，D128不能借control释放；完整view仍在H                                                    |
| restore-negative | 原生产/C完整→受损receiver的全wire门→bounded reject+H01 | 仅本提案receipt                             | 不制造restored view/roots；已有producer结果也不作为本次负例成功前缀发布；只做有限cleanup                                           |
| roots            | 借已恢复完整view+逐target/全部ref+编码+H01             | view pin与root分组票/receipt                | 重复target/head照数；只持小root列表不能声称完整view已释放；重复接收/调用用各自有限池和真实外部授权，不允许同ledger reopen          |

每钱包一个workspace arena，**全程序纯数学预检**算出其完整最大票后，将该HOLD放在首次动作之前；生命期一直到H01，不能事后用最大值倒补实际执行。arena覆盖native树/plan/cache/绑定/候选/DP/编码/limb暂存，局部数据与产物同时按票并持。R0的所有辅助域workspace合并进R0 live cap，不能拆钱包绕过原objects/scalar；Rp/R16 opaque另与R0/C/输出并持。逻辑票可保守多付但数值完整、版本固定；不声称Python实际峰值等于它。

H01在任何data动作前预付：先静态验证所有未来new handles、累计slots和唯一生命周期；release不返累计名额。control64/各D128不算新data，但仍活着表示caps/used/live/peak/stages；普通release、别名复用不能放出新余额。terminal才清control。receipt本身提前保票，成功不清；发布的native/restored/root票转移仍活着。失败则所有引用清零，累计扣费不退，账本终态不可重开。

receipt固定binary格式：`IFR2`4B+version1B+LP4(id)+input projection SHA32+handles u32+累计slots u64+两个固定0状态字节+walletCount u32；每wallet LP4(name)+按固定11域各u64（累计域=全数学需求，live域=数学峰）；childCount u32；每child LP4(id)+present u8+原ordinal u32（dummy=ffffffff）+disabled u8+按七池再十结构项的17 u64；状态u8+program SHA32；末尾SHA32。hash preimage是`I05-FEE-RECEIPT/2\0`+body+**固定32个零footer**，没有自哈希循环。receipt只证明提案数学账，不是producer receipt。

令wallet数W、child数N、非control新增handles h、全生涯slots s、完整receipt字节R，则字段ticket F=12+12W+20N；H01预付向量 work=F+3h+s+4R，scan=4R，hash=18+R；receipt保留objects=F+1，scalar=2R+32。3h覆盖生命周期proof/清引用固定槽，s覆盖所有累计槽，4R是确定四遍新receipt编码/复制票，fixed-width保证不依赖最终金额位数；自己的hash不进入自己的body。现行真实receipt编码仍pending。

invoice_model.py是通用事件状态机，用独立小票证明原子/不可退款/控制保留；它的小数学F14和这里的多钱包H01不是同一个receipt格式。本版v2完整H01向量和二进制receipt另由audit_prefixes.py独立解析/算术核验；没有拿旧小票14冒完整生产或v2费用。

## 7. 交付与执行边界

当前逐ID入口是per-id-r2.json/md；all114-fee-programs-r2.json含每ID金额、cap、首拒、paid prefix、完整来源状态、byte长度/hash、receipt实际bytes、arena/最终保留和重算配方；全program需求可精确算出，不是114个null。baseline-prefix-r2.json保存全2282事件和每prefix paid/live/peak/H，手算见hand-examples-r2.md。

一个精确新提案首拒不等于原observation接受RESOURCE_LIMIT。真实同次issuer/limits/usage/原codec以及当前I05/T05是否遵守本方案均没有验证。后继必须在另外明确实施阶段将这些primitive实际接入真实发点，并提供本表要求的独立authority；本件不改T05受审候选、不运行产品、不关闭既有平台/Job/owner/两OS/双审/CI/真人/develop门。
