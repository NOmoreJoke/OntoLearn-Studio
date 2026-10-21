# 保存恢复费用来源：独立静态准备意见

本件是方案准备证据，不是实施、运行或最终独审。仅静态读固定0475源码、固定16c API及ca099预算独审；没有 import/执行产品、测试或新API，没有写代码树、产品、测试、输入或其他文件。维护者仍T05，新API已实际交付16c，当前I05仅可申请原字节采用，不以330f待交为事实。

## 固定实际源码

当前树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-integration`，HEAD `0475d0ec6c486a63c7e8f62f11f35181da6b2576`。下列当前bytes逐项等固定Git，不靠旧记忆：

| 路径尾名 | bytes | SHA256 |
| --- | ---: | --- |
| quality/rule_profile.py | 11987 | b40b73f65f474cda32ac42caeeb837ad6470a7daeeba9013d8f69e7f0c5a261c |
| quality/rule_terms.py | 6176 | 218c4790e9b35236e393407b5b4e0207890d46fe3ea48a9a69e26aa08ddba1d1 |
| quality/rule_firing.py | 19149 | 5116aa3e96ae10e7f37eb7afddceef50879869d38af116f9c794437edf49243c |
| semantic_execution.py | 32917 | cc701dba39cdeb7f2ae281dfd4a9580b879b9e85f34d3c87a09a3414e7c32731 |
| semantic.py | 52609 | 5a3a53fc79928a7aa7de280a8477541db4053ec9b2bec489bf28a2ad4e935549 |

路径前缀均 `packages/engine/src/ontolearn_engine/`。另全文只读16c58c6的 `quality/rule_revalidation.py`，6288B/SHA9e9258cfefdef56f369dad6bb7838afd22478ea6714e4322b2d872d12616200e；ca0990的 `docs/reviews/T05/rule-batch-revalidation-implementation/independent-budget-review.md`，11562B/SHAa2bc5c2b8687f0d8697be79c1952870882bcc07a1e15e31eb8bbbef7708276d2。授权3845B/2f2ce24a已全文读取。

## 一、可以给来源证明的只是 R_parse 子域

0475的ProfileValue只作为成功firing比较证据的left/right保留；`_resolve`返回compile阶段的constant parse结果或`_one`中binding parse结果。它没有另造ProfileValue的生产路径。结果同时在 `firingGroups` 和 `mechanismBatches[*].batch.firings`重复投影，这不意味着生产曾重复parse这么多次。

建议每child一个恢复cache和一个 **Budget(该child原L_i，output_bytes=0)**，只对保存比较证据中每种不同的完整TermInput做一次canonical `parse_value(term, None, R_parse_i)`；不为普通TermInput再parse、不为每occurrence开池。不以重新compile/evaluate去填缺字段。全部非PV记录仍严格解码，随后由新批次API执行其原完整重放。

完整cache键必须区分TermInput的kind/lexical_form/datatype_iri/language_raw，以及source是否None、SourceRecord的reference/digest/revision/text。None与空字符串、source=None与四字段均None的SourceRecord、plain与显式xsd:string、raw语言大小写、同值不同source都不同。相同RDF term或数值相等不允许合并这份键。cache仅本次恢复/本child持有，生命周期结束清空，不跨任务复用发行身份。

对**同版原成功生产、字段完整未改、可信原L_i**，每个不同完整键可选原compile或`_one`中第一次parse该完整TermInput的调用作为对应；不同键不能对应同一次parse调用。原location可能非None，恢复location=None只减少check_location开销；其余输入编码、source扫描、值计算、encode_input/fingerprint发行费用完全来自同一canonical路径。故这些恢复parse的work/input费用之和是原child生产parse调用费用的一个子集：

`R_parse_i.work ≤ W_i，R_parse_i.input ≤ I_i，R_parse_i.output = 0`。

整个调用只分配已核原child份额，故 `ΣR_parse_i.work ≤ ΣW_i ≤ 16777216`、`ΣR_parse_i.input ≤ ΣI_i ≤ 262144`。disabled无batch/比较，不发虚构值；真实空batch照实恢复。失败/重试不返还已消费槽位，不按每child默认整池乘N。

这个证明的前提不是保存JSON自报的L或source：allocator/原定义/原ordered matches的可信绑定由调用者实际获得。单纯数值shape合格或摘要同值不证明来源。对恶意或被改载体，R_parse的同一硬池仍限制实际消耗，但不能保证其成功；输入/资源失败必须原子拒绝。

**只允许把上述子域写成R_parse≤W/I；整体R≤W/I仍不成立。** cache键构造、重复出现扫描、保存字段对照、JSON、载体持有与hash没有计入原parse调用，不能拿这份单射当全部恢复费用证明。

## 二、JSON真实展开界不能误用native projection的1M

`_ProfileProjection.value`的1M是native递归调用/额外容器项计数，不是最终JSON树值节点数。一个native int变为dict+hex-string两个JSON值节点，bytes变为dict+两个字符串共三个，record会增加recordType字符串；这些额外JSON节点不逐个进入原native计数。

建议恢复输入明确定义为原完整canonical payload JSON bytes及rows JSON bytes，加两个固定64字符摘要参数；两个blob实际长度总和 `B≤8388608`。若选择单JSON外壳，须另列固定外壳字节开销，不能把原payload+rows恰好8MiB的合法结果误拒为外壳超8MiB。现有两摘要和payload/rows四字段的固定外壳可用另256B保守界，但不得把其他自由metadata也塞进该常数。

以JSON**值节点**计数（object key字符另收费，不混成节点）：native projection上限M=1000000，每次最多展开三个JSON值节点；payload固定外层留64节点，rows最多10000行、每行一个string加array。因此可申请新版本恢复前门：

`J ≤ 3M + 2*10000 + 64 = 3020064`，深度上限36。

36覆盖native深度32、integerHex/bytes包装及payload/可选固定外壳层；固定schema实际更浅仍须由完整路径表核对。此为有明确推导的**新解码域**，不是默改生产1M或32。若方案坚持恢复JSON节点1M/深度32，必须先穷尽当前schema和合法production上界证明；仅引用native两个常量不够。

raw byte长度先核，UTF8/JSON词法预检先核深度、token/值节点与字符串界，再交受限解码；不先json.loads整棵树再把事后计数称为分配前门。标准JSON数字全部拒绝，整数仅canonical integerHex；NaN/Infinity、重复key、未知tag/字段、额外字段、非法surrogate、非canonical整数/hex不宽松修复。对象固定字段表每项数量与key长度另有常数界；不靠外来对象属性/迭代器或任意object_hook发行类。

## 三、独立整次R应是分域账本

建议版本 `i05-profile-restore-budget/1`，一次完整恢复持有一份整次账本。R_parse单独累计原机制单位；下面的字节/节点/bit步/limb单位须另有固定计数器，不同单位不能相加冒充CPU或RSS。每次循环/复制/比较/哈希在操作前扣其实际长度或固定结构量；所有域同时有限。

令V为保存JSON中的ProfileValue occurrence数。0475仅有上述两个投影位置，因此 `V≤2*2*32*ΣF_i =131072`。这个式子依赖实际可信ΣF_i=1024与每firing最多32比较，不能从任意JSON自报firings得出。

| 域/操作 | 硬界及前扣方式 | 合法成功的来源/未能注入原生产费用部分 |
| --- | --- | --- |
| raw输入/UTF8/词法/解析 | B≤8388608；每次原始blob完整处理先扣B；固定阶段最多四次时设byte_pass≤4B | 来自原payload+rows完整字节门；是新恢复费用，不在W/I |
| JSON shape/native records恢复/重复出现扫描 | J≤3020064；每次完整遍历先逐节点扣，固定计划至多12遍则visit≤12J；object字段查询用固定表并逐比较扣key字符 | 来自上述展开界；“12遍”仅在实现逐操作清单真不超过12遍后可用，增加扫描须更新版本/界 |
| integerHex解码 | 每项magnitude≤8192 hex digits，bit_length≤32768；所有magnitude字符H≤B，整数个数Z≤J | 来自原_projection整数门和raw byte门；全不在R_parse。canonical负号、0x前缀、零和negative_zero独立，拒bool混int |
| integer转换非线性备用费用 | 若用8 hex digits分块shift/or，q=ceil(h/8)，每项可先保留 `q(q+1)+8h+16`；整次据q≤1024、Σq≤(H+7Z)/8给有限cap | 显式包括逐渐变大的整数复制/移位；不能只收最终bit数却隐藏逐块大整数成本。若实现用受控int.from_bytes，另给其委托操作计费合同，不凭经验宣称O(1) |
| 完整TermInput键构造 | 每key使用source-presence1B+8个字段各type/length framing≤5B+实际UTF8；总 `S≤B+41V=13762560`；每occurrence都扣其全部字段UTF8扫描与key写入 | term字段是PV子树中互不重叠的原JSON出现，全部decoded UTF8总量≤B；source重复不免单。键只供cache，不取代原source/producer认证 |
| cache查找/插入与碰撞 | 推荐压缩二叉radix trie，key每bit只前进，不使用Python dict平均O(1)作证明；遍历bit≤8S，内部节点≤2U+N，U≤V；边label用不可变key span，不复制长共同前缀 | 确定性避开hash碰撞最坏桶扫描；必须逐bit/拆分先扣。若改hash buckets，须对每个碰撞候选完整key比较收费并给最坏界，不能只报正常散列复杂度 |
| cache key摘要 | 若需要审计key hash，SHA256只作标识，按domain字节+完整key逐occurrence扣；查找正确性仍以完整key trie/全等为准 | 新费用域。相同digest不证明key相同，不能以hash hit省掉source比较。hash实例仅本恢复调用，不跨child复用可信发行 |
| opaque typed bytes | 每child先用可信O_i检查lowercase/even hex长度，再解码；ΣD_i≤ΣO_i=262144，hex检查≤2ΣD字符、解码写≤ΣD字节 | 来自原机制output池；实际hash还需额外ΣD字节扣费，不因T05之后会比payload而免费 |
| payload/rows/hash | 两固定digest对原blob分别SHA，合计读取B；typed digest另ΣD；完整字段摘要只对确实可恢复的原域重算 | 新费用；inputDigest/sourceDigest缺原字节/原source形状时只能保原值并标未认证，不逆造原输入来重算 |
| 保存PV逐项对照 | 每occurrence核保存term、domain、value、language与新发行对象；字符串先len+两边字符费，整数按两边limbs先扣，Number/Calendar逐native字段严格类型和数值 | 每occurrence都收费，包括cache hit及firingGroups/batch两位置。合法相等时长度可由保存JSON推导；恶意保存短值/新解析长值仍按实际两边长度扣并受显式16k/32kbit单项界，不允许“不相等就没成本” |
| 原tuple/defs/catalog/matches持有与重建 | 每次tuple/list/record分配按项数先扣；payload中所有重复字段均解码/核同，保全false bindings顺序/when/proof | 原生产保留不支付恢复分配；不能从true groups造false。峰值bytes/对象tickets须另列，与ΣO_i不是一回事 |
| 再投影读回 | 对恢复native按同完整_projection逐出现投影，再核canonical JSON/rows bytes及各摘要；原1M/8MiB projection门仍用同值重放 | 同类型/字段同值时其计数与原对应投影一致；是新一次费用，不能借已经花过的生产projection池。新外壳/receipt另记固定开销 |

上表是可实施计费骨架，不是一段已经批准/验证的R实现。raw byte域、键byte域、bit/traversal域、整数limb域、R_parse机制单位和保留tickets应分别报告usage。若作者希望再给一个R_work标量，必须先冻结如何把这些单位换成标量的版本化系数以及每次实际委托/遍历清单，不能直接写未证的“总R≤W”。有限上界可很保守；它不承诺整个8MiB最坏输入能在120秒或给定RSS运行完。

## 四、cache命中也必须全量核保存值

每个保存PV先将完整term字段严格解码并构造全key。miss由canonical parse发行；hit只复用该新发行对象的强引用。无论hit/miss，都将保存domain与解析domain、保存language与解析language、保存value的exact类型/所有native字段与解析结果逐项比较；任何差异失败，不把重新算出的值覆盖进去“修好”保存记录。

Number须精确核numerator/denominator/negative_zero；Calendar须精确核day/second/explicit_offset/is_datetime。bool不是int；不把Number分数约分或负零转正零来接受保存字段。IRI/string/lang值保持实际str，ProfileValue永不直接从保存dict构造。cache可复用相等TermInput内容，但不宣称恢复了原Python对象别名身份；T05现API比较的是完整typed值和本进程parse发行身份，没有要求旧对象地址跨进程延续。

缓存必须在建key前对所有source字段预扣，命中后不能跳原source字节/键比较；后续新API的encode_output与check_value仍按每个出现收费，cache不减免T05三池。若cache使用摘要作索引，人工构造/测试注入碰撞必须仍分开两个不同完整key。推荐完整key radix路径使hash仅审计，不成为接受理由。

## 五、完整流程来源与剩余限制

纯恢复的成功蕴含应拆成三部分：

1. 原完整canonical生产结果成功、同版模块、相同可信原L/定义/原有序matches和未改保存字段，使R_parse子域按单射来源足够；
2. 新R结构/键/hash/逐字段比较/保留域按B/J/V/S等显式界容纳完整表示；这些不是从W/I注入，实施必须逐循环核对本表，合法production→save→另一进程restore真实跑通后才算证明落地；
3. 新16c批次API对同原L返回batch-consistent或definition-only，费用另加 `3ΣW+ΣK、2ΣI、2ΣO`。原每childL及ΣF/失败重试ledger的来源不由API或JSON shape认证。

不需要也不允许重跑matcher求新original_matches；不读取expected填缺字段；同值/摘要一致不等于原输入或producer真实。当前JSON不能自动认证所有original input/source digest域，也没有正式T01终态/项目快照/定义Catalog来源权限/保留窗口/撤回GC。它们若是正式恢复的必需前置，必须由原owner交真实不可变引用与生命周期协议，纯机制成功不得替代。

验证矩阵应以原独立手工输入的完整真实生产成功为起点，再只用保存JSON跨进程恢复；source40000/重复source、原false matches/后项错误、tight L、disabled无batch与empty真batch、全部字段单独篡改、缓存不同source/极长共同前缀/碰撞、每个R域±1/后child失败无部分输出均须验。直接构造PV、pickle或别名类不自动获得发行身份。内存原tuple即时复核、现有T05单测绿或固定摘要相同都不能代替这条路径。本件未实施或运行这些测试。

## 六、对root字节压缩前缀索引方案的静态复核

root提出的完整键字节trie可替代第三节的二叉radix方案。两者是不同实现选择，最终计划只应冻结其中一种。本节采用更保守的每键固定framing≤64B，不再依赖第三节示例编码的41B：8个native/source字符串、source-presence以及所有type/length/header必须全部包含在64B内；模块/profile身份可固定在本次调用的cache域。如果再把64hex模块SHA放入每键，就必须另算该64B，不能仍宣称总prefix≤64。每child独立cache，不跨child借用发行或parse预算。

固定 `C≤100、M≤4FC=131072、U≤M、B≤8388608`，且每个PV.term的保存子树互不重叠，得每occurrence完整key长度K之和 `S=ΣK≤B+64M≤16777216`。字段UTF8实际构造、framing写入、摘要读取均须逐occurrence付费；同source反复出现不减免。这个上界来自两位置全部term字符串在raw JSON中的实际重复表示，不能把原生产的source输入只编码一次，随后给保存记录中的任意重复编码免单。恶意记录也须先通过完整shape/节点/occurrence限额，不能信其自报F/C。

字节trie的确定性查找界成立须满足：每条edge长度至少1B，仅root可空；edge label只保存已保留不可变key的区间；沿路径每次消耗key位置严格增加；每次比较前先扣 `min(remaining_key, edge_length)`，即便首字节失配也不退费；分支使用native byte值，至多扫描256个有界索引项。成功路径edge与末次失配edge预付的总字符数≤K，分支步数≤K+1，因此每次查询 `≤257(K+1)` 索引/字符检查单位足够。整次可给明确新域 `R_cache_query≤257(S+M)≤4345430016`。这是很松的抽象debit上界，不是43亿次实际运行保证，也不承诺CPU时间或RSS。

miss至多U次；压缩trie每次插入新增至多两个node，可给保留node tickets `≤2U+C≤262244`，不含PV、JSON、native records等其它对象。每次split的“≤512”只能表示复制branch索引引用的单位上界，整次该域 `≤512U≤67108864`；另须按实际结构冻结新node/edge元数据分配、固定容量branch数组slot分配与清零、父链接改写和key-span引用建立的固定收费及硬上限。边label若复制字符串/bytes切片，而非保留key区间引用，本界不能覆盖长共同前缀的复制，须改实现或另收实际复制字节。持有全key字节合计≤S；decoded source字符串、记录对象与新发行value同时存活仍另付retention，不能拿S冒充总RSS。上述index单位≤512U也不能当所有split操作的总费用。

SHA256(fullkey)只作审计，不参与cache等价判定。每次出现对domain separator与完整K字节另扣R_hash；若固定separator长度d，整次 `≤S+dM`，d须在版本中固定。相同摘要的不同完整key依然走不同完整字节trie路径；不能假定collision-free，也不允许凭hash hit跳source键比较。

还需独立覆盖top firingGroups到child slot的rule_id查找和allocator对照。term cache的257(K+1)没有支付这些操作。可选在≤100个可信rule_id上另建同样有界前缀索引（其构造/lookup/retention独立按实际完整rule_id字节付费）；或逐项线性全比较并用 `查询数×100` 次、每次两侧完整字节长度和作硬cap。任一方案应由实际原生产capture的allocator提供child/rule对应，JSON不得自行声明可信slot或L。原API本身不认证原调用的收费账本；缺原生产capture时，不得以这个trie的有限界补写“任意历史成功均保证恢复”。

本节仅静态推导新的cache子域。它不冻结第三节尚待逐循环盘点的byte_pass/visit常数，也不替代完整record/hex解码、逐PV重新parse及保存domain/value/language核同、false matches顺序、typed bytes、metadata摘要与retention各自的硬cap。最终计划若采用新的JSON展开节点/深度域，必须明示其版本和展开推导；若坚持8MiB/depth32/1M均是JSON而非原native门，则成功→恢复前提必须额外要求该具体保存JSON本身满足三门，不能从原native投影成功直接推出。
