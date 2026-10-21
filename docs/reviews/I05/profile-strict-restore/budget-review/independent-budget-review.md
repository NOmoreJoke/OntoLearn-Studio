# bbd79c3 独立实际预算与持有审查

审查者 `/root/restore_budget_code_review`。结论：**本固定候选尚不能给出“实际预算与持有来源全部通过”**。循环、完整 key/trie、整数分块、R_parse 子域与16c分池的主要来源可建立；encoder 的“两份 buffer”局部持有论证与实际执行不符，projection 返回后的新增 scalar 和固定 metadata 的普通 live 归属也没有在代码中完整落明。后两项未构造整次恢复突破总 cap 的反例，不能据此升级为已确认 P2 产品漏洞，也不能用 cap 很大宣告证明通过。需修显式 reservation 或给出同口径的完整同时持有分配证明后复审。

## 1. 固定身份、授权与实际检查

- base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；Git source `bbd79c3cff88e8fef348a9c4dcb6981ab5e3cb47`。
- `packages/engine/src/ontolearn_engine/semantic_profile_restore.py`：47127 bytes、1213行、SHA-256 `8a09474ee3f5c71b9b4205df8ee590106bad34ac6ad01c06ee9f310c84487889`。
- `packages/engine/src/ontolearn_engine/semantic_profile_restore_budget.py`：37212 bytes、1116行、SHA-256 `95b170ab99220d8d602d87a321bae481774806dc2bc11b760b4933e866f51c16`。
- 两者均从 `git show <固定ref>:<path>` 全文读取；生成 audit 时当前文件逐字等于该 ref。报告行号只指上述 Git bytes。简称分别为 core、budget。
- 全文读授权 raw、AGENTS、developer-common-instructions raw（含完整第九节、无桌面/外审约束）；逐行读 approved-plan raw §6、6.0、6.1、6.2。具体 bytes/hash 在 `audit.json`。
- 读实际被委托的 `_ProfileProjection`、`_profile_json_bytes`、canonical Budget/typed walker、parse_value/issuance、numeric/calendar bounded helpers、compile/evaluate 中 PV 来源、16c API 三池与 control 源码；这些依赖相对 bbd79 无工作树 diff。
- AST 枚举两文件全部71个 for/while/推导式（含模块期固定表生成），完整源码片段、函数归属、起止行在 `actual-loop-inventory.json`。无截取列表充当全部检查。
- 自有 stdlib probes：`counter-probe.py.raw` / `counter-probe.json`（原预算模块完整隔离执行）；`encoder-peak-probe.py.raw` / `encoder-peak-probe.json`（固定原 encoder 的实际 primitive 分支）。均用系统 Python3.9.6、无产品 import、无共享虚拟环境。它们不是完整 engine/restore 或受支持 Python3.12 集成证据。
- 未重新执行生产/restoration 139测试、93 exec child。根提供的最终测试 ref `94d5c38dc5e3989823145f5b402529195de93cbf` 与原134pass/5fail留档、N100原生产 resource failure 为外部上下文，未当成本审独立实测或源码数学证明。
- 本审仅写 `budget-review/`；无产品/测试/68输入/环境/AGENTS修改，无commit/切分支/GUI/CUA/Electron/e2e/HMR/Keychain/模型/付费/push/PR/merge/Goal。不是指定双模型审查或CI。

## 2. 逐意见：来源、分级、触发和边界

### BR-01：encoder 两 buffer 局部上界不成立（已确认的预算证明阻断）

位置：budget:755–778，尤其761 `reserve(scalar,2*bound)`；实际既有 delegate `semantic_execution.py:593–607`。

`_profile_json_bytes` 每轮同时持有 `chunk` str、`data=chunk.encode('utf-8')` bytes、`output` bytearray。`output.extend(data)` 后，尚未进入下一轮时这三个局部都在。若一大字符串主导输出，其 UTF8 载荷约 `3*D`，超过 `2*D`。最后 `bytes(output)` 还会与 output 同时存在；循环最后项的小 chunk/data 也未主动 del。

独立 probe 执行的是固定 Git 函数原 AST，真实 stdlib JSONEncoder。20万ASCII字符：最终200002B，三个局部同时600006B，超过2×输出400004B；4万NUL：最终240002B，三个局部同时720006B，超过480004B。原函数实际line601的trace记录在证据JSON。测的是逻辑UTF8载荷，不是RSS，不测CPU，未计原值或对象头。

因此 A11–A15 若仅以 `bytearray+bytes≤2B` 支付整个 delegate 临时，就遗漏 chunk/data。计划 opaque 每槽文本≤65536 的来源也不能覆盖240002B的escaped chunk，且计划已明确将此类chunk归普通buffer。**这是局部来源反例；未证明整次恢复普通 scalar 总 cap 被突破**：AST 对字符串保留4×token的保守余量可能覆盖部分实际载荷。未经逐集合证明，不能把此余量隐式当已转票。

处置要求：调用前显式预留覆盖 chunk str（统一按4B/codepoint时从严）、data、sink、最终bytes及常量；返回时转为结果 len+1 持有，异常释放。无需改变固定cap，也不得改旧canonical writer。根提出 `8*bound+64` ordinary scalar 方案可覆盖固定实际 delegate（4bound chunk + bound data + bound sink + bound final bytes + 常量），仍需在新SHA核具体时序。

### BR-02：projection 新 scalar 返回后普通live归属未落明（待证明；不定P2产品漏洞）

位置：core:938–948、1020–1056；实际 projection 的 int→hex、bytes→hex、str.encode 分支。

`_project` 前付对应 A 行 work，并普通 reserve objects=2J；`opaque()`退出即释放全部 opaque scalar，但 safe tree 中新生成的 integerHex/byteshex 字符串继续由 safe_reason/safe_defs 等持有。没有 ordinary scalar reserve/transfer 与 consumers 的释放配对。str 分支临时UTF8编码也非一概≤65536：warnings/basis/termSources.term 可经 decoder.string 默认门接受比65536更长的文本。

这不自动证明总cap不够。解析每个value string已留4×token scalar，raw/hex/native其它票仍在；单份safe新增hex可在该余量内。但这是额外跨生命周期重用，当前代码/注释没有给出所有并持集合的无重叠分配证明。本审不以 helper 脱离整恢复前置条件的低cap例伪称真实绕过。

足够的显式修复来源：每次projection新hex总字符≤其对应已验证wire token bytes≤J；str返回原str，只会临时UTF8编码，累计此前新hex≤J加一次当前UTF8≤J。调用前普通scalar 4J足够；同2J objects保持到safe树消费者del，再release；失败时释放。A7 safe_reason与A8 source/defs最多两份并持，≤8J新增scalar，不扩固定cap。新代码仍须复审。

### BR-03：固定 metadata 的前分配/并持收费未完整映射（待证明；不定P2产品漏洞）

精确路径：

1. core:679–697：graph_budget 先产生 limits dict、临时 ProfileLimits(**entry)、usage dict，697才reserve19；外层reasoning在870提前reserve19，是否可暂支付内部新增对象再转外层dict，未证明。不能仅看单条后置reserve便宣称突破总cap。
2. core:767–770：values dict在769 reserve42之前构建，之后ProfileLimits/Budget/caches临时、lists引用需统一计；begin的17N是入口固定context，不应无说明重复认领。
3. core:1057–1096：parse_usage tuple及两个list先于1059 reserve；8N+2普通objects没有解释怎样支付按make同口径的 RestoredChild 9字段+record、caps四组pair及外层tuple、列表槽和最终tuple。core:1203–1213在cleanup/finish后才构建RestoredBatchSet，无法再用running ledger保护该分配。A16未prepay；少量traversal只付child循环与slot。

固定metadata总cap2048N+4096很宽，但cap不是live。实际small metadata多付或其它保守tickets可能覆盖；当前没有完整分配证明，因此不能批准“每一次实际前分配都已落地”的严格合同。建议把固定metadata reserve/charge前置并保持至receipt构建完成；receipt在try内running时构建，最后收费/reservation完成后再快照usage/peaks，finally只drop/cleanup/finish，最终仅return。

根提出 graph64objects、parse setup64objects、A16预付块及256N+256objects、1024N+1024scalar/copy、128N+128 traversal 在本固定结构下保守足够，但本报告不对未出现的新SHA给通过。

## 3. A1–A16 与真实操作的映射

以下是实际操作审计，不以阶段名本身证明费用。J在实现中取B+Q的原byte上界；`json_nodes`才是实际物理value/key数。U≤M、N≤100均为跨child总数。

| 阶段 | 实际路径/操作 | 收费、委托、持有与结论 |
|---|---|---|
| A1 | budget:474–742；core:960–990 | UTF8前付wire/copy len、scalar4len+1object；预留4096objects+16384scalar固定scanner栈；一次preflight、一次build，分别前付wire len。preflight统一physical node计数与depth35；build逐node/fieldslot/arrayappend留票。字符串先走length/Unicode门，value再留4token scalar、copy token后scanstring。keys≤64、每对象≤32，scanner固定栈覆盖bounded临时；固定候选比较和duplicate完整key比较均schema前扣。失败在昂贵第二duplicate值前停止。raw Turtle只UTF8。 |
| A2 | core:276–705 | exact位置schema固定dict keys、string逐ord宽度、integerHex、byteshex、collect/make native。collect先付items列表+tuple临时，tuple完成释放list部分；make先reserve record+参数槽并visit；int/bytes见下文。新string返回既有str，未复制文本。graph metadata见BR-03。 |
| A3 | core:706–889；899–1001 | 原allocator的IDs有界插入排序、disabled线性找、17limits逐项divmod核原L；每次id比较按两边总长rule前扣，位移按references前扣；child按ordinal直接索引，完整Catalog/defs/limits跨联按_same付域，不按alias免单。固定metadata问题见BR-03。 |
| A4 | core:471–505；budget:849–1116 | 每个PV descriptor完整重建；full term key/source八字段+source存在位；每occurrence key、audit hash、triequery、saved-vs-fresh完整比较。只有miss进parse；parse前cache保留lenkey+65536scalar/16objects，opaque与同child原L parse pool；hit不重parse但仍逐字段比较。见下面索引/单射证明。 |
| A5/A6 | core:859–865 与_same | top groups逐项与child firings比，两个已在wire的树都付字段/字符串/limb；首不等终止。A6无第二整树函数调用，而是_same读取右侧所付lenright/field/ref。不得因没有A6标签称免费。 |
| A7 | core:1020–1021/_project | 原native reasoning整树projection；前付32J traversal、128J fixedkey/schema、4(B+Q+S)copy；ordinary2Jobjects、opaque一调用在途；scalar归属见BR-02。 |
| A8 | core:1022/1028 | 同一projection实例source后defs；prepay(A8)一次，source来自独立Q、defs来自B，累计≤J；source结果消费释放后才defs，不各领独立J work。safe_reason持续在途。 |
| A9 | core:1003–1019 | Turtle每个termSources.source完整对同一source，B中每occurrence已有该source，重复比较按copy两边实际长度付；structured三项分组建records/source引用tuple，先objects2*occurrences+2和traversal len，再_same完整字段。无parse全部termSources。 |
| A10 | core:1036–1042 | structured records第二个原projection；独立一次prepay；其safe树一次消费，持有问题同BR-02。 |
| A11 | core:1049–1055 | 固定safe_payload dict先reserve9；canonical writer前付A11，wire对照payload前扣len、_same copy两边长；encoder临时见BR-01。 |
| A12 | core:1105–1126 | rows先sequence，prepayA12；编码payload decode前scalar4len，逐8192字符slice/比较属于该块加实际_same；rows canonical再次调用同stage不重领J work，二者累计固定表范围；wire对照rows另付len。slice在text释放后可能留最后chunk≤8192，固定栈/元数据余量须明确容纳；不是RSS计数。 |
| A13 | core:1023–1035 | source、defs canonical累计一次prepayA13，不同时持两个版本；source逐字对独立前像，defs hash另域。encoder临时见BR-01。 |
| A14 | core:1043–1048 | 仅top Catalog编码一次/hash，child Catalog已按其每个wire出现核同；不N次编码top。 |
| A15 | core:1038–1042 | structured记录canonical一次对独立input前像；source复用A13，未做第二source重建/parse；wirelen和copy两边长前扣。 |
| A16 | core:1057–1096、1194–1213；budget:374–405 | 所有恢复/rows/hash完成后每child一次start→16c→complete；无yield或外部写；最后才返回。16c pools独立，见下文。失败cache.drop/ledger.cleanup/finish(False)不再耗work，终态防复用。metadata/receipt后构造票据见BR-03；不能宣称本版本已满足完整前分配合同。 |

## 4. 逐循环、比较、hash、UTF8、hex与索引来源

### 4.1 71个循环/推导式逐项覆盖表

完整AST实例见JSON，表中每个起始行都可对照实例；固定模块初始化不处理输入blob，位于一次恢复ledger生命周期之外，不冒充运行期免费处理攻击数据。

| 文件/行 | 实际循环 | 付费/上界归属 |
|---|---|---|
| core63、212 | 模块期17项limits/字段表 | 固定class-owned常量；不扫描wire。 |
| core243、248、251 | tuple/list item、17类分派、字段槽 | _same逐call traversal1；两边长度；固定表len17与字段len先付；str/bytes两边长在domain前付，整数按limbs，eq后不退款。 |
| core280、299、317、343、351、425 | 固定schema keys、native collect、ord、sha字符、4source、3Catalog | schema64*(keys+value+1)；sequence1+n/collect refs；copy len；sha schema64；source/Catalog各调用自身收费helper。 |
| core551、553、596、598、608、678、679、685 | comparison/head位置、17limits/6usage/5graph表 | len比较/heads前traversal；object fixedkey/schema和每int费用；graph固定分配前门BR-03。 |
| core720、726、745、750、757、767、776、803 | allocator插入/disabled/17字段/values/findslot/childlimits | rule按实际ID两边长及插入位移；17N固定field；每lookup最多N，不靠dict/hash；values前门BR-03。 |
| core838、845、854、860、863、868 | top definitions、children、topgroups、childfirings、ordinal | wire对应occurrence范围；collect/native sequence、find_slot、firing、_same收费；ordinal前traversal len。无未在wire反复重建top。 |
| core892、911、921、994、996 | caches清理、6digest、3identity、metadata | cache清理由预付node/update供给；固定metadata的copy/sha/schema/_same；上限N或6/3。 |
| core1005、1012、1013、1017、1050 | source对照、records三组引用、sourcevalues、safe_payload | A9 len occurrences预付和完整_same；2*occurrences+2 tickets涵盖分组/引用；safe_payload9票；固定7keys。 |
| core1057、1061、1114 | parse_usage、slot、rows | A16 metadata BR-03；slot前visit；rowsA12预付加每row实际visit/_same。 |
| budget135、223、232、284、393、403、447 | 固定stage、overrides/去重、cap下调、finish状态、cleanup、caps快照 | stage表16；domains17；overrides仅17项、拒上调；不依赖wire；slot检查最多N，固定元数据工料应由A16/入口块说明。 |
| budget509、554、620、634、652、667、673、704 | whitespace/string、4hex、fixedkey、3literal、objects/dups、arrays | whole lexical/build各wire len前付；hex4另copy4；固定schema每候选两边len+1；duplicate最多32完整键；depth/node gates；build reserve每node/slot。 |
| budget804、813、840、854、896、906 | hex字符/8hex合并、byteshex字符、UTF8尺寸、8key字段/写入 | 整数 q(q+1)+8h+16前付；copy lenhex+decoded；_text_size copychars；key framing/encode/copy前付且scalar2K（sink/bytes）留票。 |
| budget1046、1055、1069、1102 | trie路径、≤256branch、span、linked clear | query1、每candidate1、span预付；position严格前进；clear按每node预留metadata及miss更新，实际断开next/children/value/key，耗尽后无需新debit。 |

### 4.2 scanner与wire/node数

`read_json` 实际只有两次 `_Reader.read`。原注释/截断命令不能当第三遍证据。字符串内部自己词法扫描；build非key值在scanstring前付copy token，固定key两轮受≤64和固定stack gate，schema完整候选比较另域；scanstring无object_hook/callback。native数值/NaN/Infinity从第一pass拒；UTF8 strict先decode失败释放自身票；surrogate pair显式hex4门。

独立budget probe对 `{"format":[true,null]}`：json_nodes=5（root/key/array/true/null）；build traversal8（5node+1fieldslot+2arrayappend）加begin17；wire恰3len（UTF8、preflight、build）。duplicate第二个format在进入70000字符value之前拒，json_nodes4。物理node实际count不是直接伪报J；J=B+Q作为sum cap，上界因为每value/key在wire至少占一byte，Turtle不计JSON节点。

原blob读取包括UTF8/双reader、payload/rows canonical字节对照、input/source前像对照，实际debit记录对应这些调用；rows的native text decode/slice归A12预付copy，而非再计原blob的额外wire pass。库scanstring的token处理归copy/固定栈，不得再声称逐C内部byte触达都有hook。六倍wire cap是抽象pass合同，不是机器级read计数。

### 4.3 hex与一般比较

h≤8192、q=ceil(h/8)≤1024。正则/十进制大int未用于恢复；先integer域付q(q+1)+8h+16，再逐char检查、小块int(piece,16)、left shift/OR。每块j的shift+OR有≤2j的32bit-limb处理，Σ2j=q(q+1)；roundtriphex/符号与扫描由8h+16保守余量支付。Σq≤Σh、q≤1024，整域≤1049Σh≤1049(B+Q)<2048(B+Q)。value最大4096B，旧/shift/OR等最多约三份、回编码8195字符与最终值的峰值分别<4*4096保留块；最终只留size+1obj。失败释放完整临时，不退work。

hex_bytes先验证even/decoded≤同原child.output_bytes≤262144，再copy lenhex+decoded，逐char lowercase后reserve decoded+1再bytes.fromhex；不接受native arbitrarybuffers。_same无任意dataclass反射，固定17类、字段完整，str/bytes/long common prefix事前两边len，整数按32bit limbs；每occurrence包括alias都付。

### 4.4 完整key/trie与每次重复source

K=8B header+1 source-present bit+8*(1 presence+4 length)+ΣUTF8=49+ΣUTF8。None与空串、source None与SourceRecord全None区分；UTF8编码单射，固定字段序与长度前缀无歧义。kind受iri/literal；source四字段每次都扫描/编码/写入，不因alias或同source减费。每个PV.term子树在保存wire不重叠、字符串decodedUTF8≤原token bytes，framing49由每PV64余量支付，故 ΣK≤B+64M=S。

get_or_insert每lookup付16alloc、record occurrence/total K、hash(separator32+K)，hash不用于相等。分支先付1再比首byte；edge先付span，逐byte比较；首byte与span重读分别已付。每次已完全匹配edge使position至少前进1，沿路径最多K+1轮；branches≤256，Σspans≤K，初始query1，合≤257(K+1)，跨occurrence≤257(S+M)。末失配span保守已付不退。

split仅改start/end并引用完整旧/新key，无后缀slice。每miss最多2nodes，roots N，nodes≤2U+N；每node预扣320、reserve1node/256slots；append每次按完整旧vector len≤256预付refcopy，每miss最多两append，≤512U。miss另64，lookup16，对应alloc表。linked清理总nodes/edges≤2U+N，node320中64metadata与miss64更新足够支付固定字段置空/edge decref；不借耗尽query池，也不递归。

独立synthetic-byte probe插入256同前缀末byte分支再逐一hit：256miss/256hit、nodes258≤513；factory只256次。另lower trie_nodes=3在split中失败后clear确能归零所有nodes/slots，不退款。它只证预算/index，不证真正canonical PV发行。

### 4.5 rule/ID与hash

rule ID总字符≤B；每query最多N候选，待查ID≤B，所以比较总≤(N+1)B≤101B。插入排序按N个查询摊、disabled≤N、top F≤1024、入口核同固定余量；重复top目录遍历由每child wire occurrence支付，非N次无wire重扫。实际sorting每比较运行两次关系运算，其总扫描≤lenleft+lenright，已付一次两边长度足够。

外层hash实际调用：payload+rows=B；input+source=Q；每child typed payload总D≤262144且D≤B；definitions+Catalog≤2B；每key一次S+32M。当前无额外structured二次hash、无可选payload/rows再hash。合≤4B+Q+S+32M（固定receipt/context余量另65536N），低于32B+8Q+S+32M+65536N。digest预付hash len再sha256、hexdigest留64+1；cache audit也先付separator+key，结果替换先留新后释放旧票。canonical parse/16c内部fingerprint由各自Budget收费，不是外层hash免费。

## 5. R_parse、16c、同时持有和失败清理

### R_parse 只对同child唯一完整term单射

每child一个parse pool，ProfileLimits来自独立捕获的原divmod L，仅output_bytes置0；不同child不共享cache或池。完整term含source/raw语言/None形态；只有cache miss调parse，不能以canonical value数值相等合并不同term。0475的saved PV仅来自成功firing comparison operands：常量由compile的对应operand parse；bound变量由_one该match对应binding parse。不同完整TermInput不可能单射到同一次parse调用；即使同term多处出现，恢复miss最多一次。location None省掉原位置检查，不增加canonical term发行工作/input；encode_input结果不含location。

故对**同次成功原生产、同版实现、完整可信原L/输入捕获**前提，R_parse_i work/input可注入原W_i/I_i子集，output0；不对termSources/原图IRI都parse。篡改输入可在该池安全失败，不承诺成功。source witness、JSON、index、hash、copy、外层retention不在此证明。**没有整体R≤W/I结论。**

### 16c三池与restoration分开

core:1061–1073每slot只调用一次check_firing_batch，同原L；disabled仅明示映空matches并保原None batch。实际16c `_Resources`有replay、saved_encoding、saved_issuance三个Budget，control先entry再bind；compile/evaluate重放全部false/true matches，保存typed encode与PV issuance校验各池独立。K=1+33F_i+4O_i+128+70+4，对应实际API常数profile长度35、digest64。因此cap为3ΣW_i+ΣK、2ΣI_i、2ΣO_i。restoration各域和R_parse没有塞进该三池，也不每group重开池。

### ordinary/opaque held sets 与局限

- raw B+Q入口票持至结尾；decoded UTF8临时4len，read_json finally归还；AST保留每node/slot及字符串4token；native records/collect/ints/bytes/descriptor按普通票积累，字符串原引用可复用但每occurrence工作仍付。
- cache持有全key、新发行PV/指纹/weakref相关固定数据；miss65536+lenkey/16object普通预留在factory前，opaque覆盖parse内临时，原Budget照常。key/sink临时2K及temp field refs；cache key ownership与temporary分开，调用者finally release_key。cache保持PV强引用直至所有API结束。
- safe_reason持续持有，source→defs→records依次消费；最多两份safe tree；2Jobjects每份，原AST/native/records构成计划8J框架。新增scalar归属BR-02；不能只复述16倍大cap。
- canonical返回结果保留len+1，在下一版本前释放；BR-01指出encoder内部局部并持须修来源。rows text+最后chunk、encoded payload/rows并持须同该普通块核算。
- opaque只允许一个调用在途，完整declared peak事前reserve，即便override更小也必须失败；先scalar成功但objects失败会归还scalar，正常/异常finally均释放。typed walker最多32层，数字helpers迭代、临时bits≤32768（4096B），typed sinks/本地重放由8(ΣI+ΣO)支付；此为固定源码逻辑载荷模型，不含C regex/allocator/解释器/对象头/RSS。BR-01/02的大JSON文本应由ordinary reserve支付，不能强塞≤65536小槽来源。
- 本审不把usage/caps相同当实际成本证明。usage是已成功扣除的抽象work，失败尝试超过cap时不记录超限请求，也不退之前usage；peaks是logical reservation峰值，可能保守，非RSS/CPU。当前BR项意味着这些peaks尚缺完整所有实际临时/返回载荷映射。

### 失败与发布

所有child重建、PV比较、projection/canonical/rows/hash完成后才进API循环。API先start_slot，成功complete；children只是函数局部list，没有yield/callback/publication。最后slot失败时函数无返回；外层重建有限RestoreFailure并在except外raise，原带raw数据traceback没有串到新异常context。decoder.drop逐cache断开真实引用、清pools/children/rows_json；随后cleanup只降live、finish false将槽全部failed；成功才返回单一冻结result。结果传出可继续持有PV，属于明确transfer，不是内存凭空消失。

失败清理不调charge，nodes释放有实际计数，普通未逐票释放部分由owner栈已退/引用已丢或结果transfer后cleanup归零；不会为退款重开池。同ledger在入口state!=new前拒，保留其原terminal usage/state；新ledger是新纯操作，不声明持久防刷/重试权威。probe实测budget层终态防复用、usage不退款、split后资源失败清零。完整末slot原子性来自代码审计与根测试上下文，本审未独立跑engine集成。

## 6. 复审条件与有限结论

需要新固定SHA使BR-01普通encoder峰值、BR-02projection retained scalar、BR-03metadata前分配/receipt construction有显式reserve或完整无重用矛盾的同时持有证明；核收费仍在固定cap内、普通release只在实际引用drop/transfer后发生、usage/peaks快照位于最后收费之后。纯扩大cap、把恢复费塞进原Budget、删source/false/head、减少schema检查均不能关闭意见。

本审没有发现完整key碰撞等价、trie尾切片、R_parse非同child重领池、16c与恢复混费、最后child部分返回的代码路径；这只是本固定范围结论。未测8MiB最坏CPU/RSS，不保证512MiB/120秒，不取代指定双模型、CI、跨OS、正式producer/selected或持久保存授权。N100既有原生产资源失败不在此改称恢复成功。修复后本报告保留原SHA身份，不能直接改写为新候选通过。

原探针脚本执行后按根要求仅重命名为 `.py.raw`，脚本字节与原hash不变，避免全仓ruff将诊断副本视为产品源。可用 `python3 <absolute-prefix>/counter-probe.py.raw` 或 encoder 对应路径复现；输出原件未重写。
