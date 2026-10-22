# 0475 保存表示盘点：纯恢复方案的静态输入

本件只做字段和表示盘点，未 import/执行产品、pytest、比较器、图算法或新 API；未改0475产品/测试/输入、未创建代码树、未消费API。它不是独立完整方案的通过报告，更不是P1/P2或正式selected通过。只向主开发提供本轮准备证据。

## 固定源码与方法

实际当前HEAD为 `0475d0ec6c486a63c7e8f62f11f35181da6b2576`；开始时仅保护AGENTS dirty。下列0475工作区字节逐一等固定Git blob；用标准库AST解析，不执行结果。新API只读固定 `16c58c6d0ca56491c7134c4866f9bed5e0f722c5`，不沿用“330f尚待交付”的旧事实。

| 路径 | bytes | SHA256 |
| --- | ---: | --- |
| `packages/engine/src/ontolearn_engine/semantic_execution.py` | 32917 | `cc701dba39cdeb7f2ae281dfd4a9580b879b9e85f34d3c87a09a3414e7c32731` |
| `packages/engine/src/ontolearn_engine/semantic.py` | 52609 | `5a3a53fc79928a7aa7de280a8477541db4053ec9b2bec489bf28a2ad4e935549` |
| `packages/engine/src/ontolearn_engine/semantic_turtle.py` | 33916 | `4180feb9d0c775669b65338e1cfb37a8d5bb7f3ce155b4804dd53a43efad5214` |
| `packages/engine/src/ontolearn_engine/resources.py` | 2927 | `2361c55da7983e46fbdd08e50fc3ec48b281d2c76d0021f82fd94ab50ca54274` |
| `packages/engine/src/ontolearn_engine/quality/__init__.py` | 548 | `9a5130c2fdbe376e5e4c15e68085f01724847ff13e9b2c195cf270e476806d9c` |
| `packages/engine/src/ontolearn_engine/quality/rule_profile.py` | 11987 | `b40b73f65f474cda32ac42caeeb837ad6470a7daeeba9013d8f69e7f0c5a261c` |
| `packages/engine/src/ontolearn_engine/quality/rule_terms.py` | 6176 | `218c4790e9b35236e393407b5b4e0207890d46fe3ea48a9a69e26aa08ddba1d1` |
| `packages/engine/src/ontolearn_engine/quality/rule_numbers.py` | 7372 | `6b080a55bd8f4af1a1120b55448e02a1a442c231a32ab575ce6e82de054164f9` |
| `packages/engine/src/ontolearn_engine/quality/rule_calendar.py` | 4047 | `6a2e43b029f7069e398f696ff19948d9e806f06fecd9a1e239b889a55e528aec` |
| `packages/engine/src/ontolearn_engine/quality/rule_comparator.py` | 1750 | `9a495876a182d1cad4cac86bb4651c1627e4afc37e1bf9bb3d62be6bb0e95ff2` |
| `packages/engine/src/ontolearn_engine/quality/rule_firing.py` | 19149 | `5116aa3e96ae10e7f37eb7afddceef50879869d38af116f9c794437edf49243c` |
| `packages/engine/src/ontolearn_engine/quality/rule_revalidation.py`（仅Git只读16c） | 6288 | `9e9258cfefdef56f369dad6bb7838afd22478ea6714e4322b2d872d12616200e` |

实际读 `_ProfileProjection`/`_profile_json_bytes`/`_execute_profile` 全路径、reason的返回与child组装、七机制记录/typed编码、parse/check_value及新API完整184行。仅参考当前字段事实，未复用旧运行通过来替代本轮证明。目录/字段行号依据固定0475：semantic_execution.py:502–732、semantic.py:1040–1118；quality/rule_firing.py:41–153、rule_profile.py:18–141/270–377、rule_terms.py:46–179。

## 一、哪些数据已完整投影

`_ProfileProjection` 对已批准record保留 `recordType` 和 dataclass全部字段；int统一为 `{"integerHex": hex(v)}`，bytes为 `{"encoding":"hex","bytes":...}`；tuple与list都成为JSON array。它没有发行/原对象引用表，也不是解码器。

| 机制record | 必须精确还原/核对的字段及容器 |
| --- | --- |
| SourceRecord | reference,digest,revision,text；每项str或None，None与空串不同 |
| TermInput | kind,lexical_form,datatype_iri,language_raw,source；source是None或完整SourceRecord，不RDF归一化 |
| Variable | name；仅允许规则模板位置，不允许混进ground match/head实例 |
| Triple | subject,predicate,object；规则模板的subject/object可Variable，predicate为TermInput；实际when/head均ground TermInput |
| Comparison | left,operator,right；按原定义位置，operand只TermInput或Variable |
| RuleSpec | rule_id,when,comparisons,heads,source,revision,definition_digest,policy；前三数组字段还原tuple，定义原顺序不变 |
| Catalog | classes,object_properties,data_properties；三tuple原顺序保留 |
| BindingMatch | rule_id,bindings,when,proof_leaves；bindings为tuple[tuple[str,TermInput],...]，when为Triple tuple，proof为tuple[tuple[str,...],...]，false/true都保原顺序 |
| ComparisonEvidence | index,left,operator,right,result；left/right最终必须是真实重新发行ProfileValue；index精确int、result精确bool |
| HeadEvidence | index,triple；全部head出现和顺序保留，不按相同fact去重head |
| PreparedFiring | rule_id,bindings,when,proof_leaves,comparisons,heads,basis,source,revision,definition_digest,policy；上述ordered tuple和全部metadata完整 |
| PreparedFiringBatch | firings,facts,payload,digest,profile；firings/facts是tuple，payload是真实bytes，digest/profile精确str |
| ProfileLimits | 17个固定字段；exact int拒bool，每项0至固定默认上界，不从动态字段反射或保存JSON取得“可信限额” |
| ProfileValue | term,domain,value,language；term完整，domain/value/language必须与当前canonical parse(term)逐字段全等 |
| Number | numerator,denominator,negative_zero；前两项精确int，denominator>0，末项精确bool；保留负零标志，不能仅按分数相等 |
| Calendar | day,second,explicit_offset,is_datetime；day精确int，second为完整Number，两标志精确bool |
| InputLocation | section,index,side,span；只有该位置允许record；span为None或二元tuple。成功payload并不凭此生成真实byte span |

完整返回里同时保 `firingGroups` 和各child `batch.firings`；全部原 `originalMatches`、原 `definitions`/`catalog`、原限额及原预算用量已在child载体。没有缺失false matches，不能再写“仅true组已保”。不需要恢复 `_CompiledRule`、`CompiledPlan`、seal、weakref、旧进程对象id或旧Budget运行状态；这些本来不是JSON采用面，新API会fresh compile。

child的以下差异必须保持：disabled=true时 `originalMatches=None`、`batch=None`，但definitions仍是其实际单规则且原compile已完成；启用空定义dummy child为ruleId=None、definitionOrdinal=None、definitions=()、originalMatches=()，实际空PreparedFiringBatch存在。恢复器不能把两类None都改为空batch。给16c API的disabled definition-only调用需要在独立本地适配中明确把“原未evaluate”的None映成API要求的空原matches参数，并保外层原None，不能宣称它原本发生过evaluate；该适配只作用参数表示，不伪造原匹配。

## 二、严格白名单解码可以补回的表示

tuple/list标签丢失不是自动不可恢复。以固定format2的字段schema规定容器类型，可在每个允许位置把JSON array变成exact tuple或保留list：RuleSpec/Batch/Firing/BindingMatch/Catalog等机制字段全有固定tuple规范；rdfs/rules/evidence/rows等外层投影列表保持各自固定list。不得做“所有array统一tuple”或由传入recordType动态import类。只硬编码当前canonical模块/类与字段集合；`_CompiledRule`/CompiledPlan不允许出现。位置不允许的合法recordType同样拒绝。

解码前先对原bytes做有限长度与UTF8门，拒重复JSON键、NaN/Infinity、额外/缺失字段及非批准tag；避免json.loads默认覆盖重复key。在本格式的payload及result封套内，所有生产整数均是integerHex wrapper，原生JSON number（含float、exponent、-0）应拒绝；bool不走int路径。integerHex只允许canonical `hex(int(text,16))` 的原样结果，拒多余前导零、`-0x0`、大小写/符号变体；先限hex字符数/bit上限再分配整数，不改进程decimal/int全局政策。bytes同理只允许固定二字段、偶数lowercase hex并先检查decoded byte上限。字段处另施更紧bound：head/comparison索引、ordinal、limits、Number位数等，不能仅全局32768bit就通过。

要特别分开三种计数。0475的depth32/1M nodes是原对象投影函数的语义访问计数，JSON还新增recordType/字段名、integerHex和bytes wrappers，封套另加payload/reasoning层。不能不定义根和边就把depth32套到wire。通用投影上界可保守导出“原语义32+outer result/payload两层+integerHex一层=35条物理边”；这不是声称当前固定schema实际可达35。对本件全返回四键schema可收紧：root execute-result在depth0，最深合法路径为 `payload/reasoning/mechanismBatches/[child]/batch/firings/[firing]/comparisons/[comparison]/left/value(Calendar)/second(Number)/numerator(integerHex)/integerHex`，标量在14条边、container最深13；right与denominator同界。完整schema应逐分支核此派生表。wire AST节点也不等于原1M计数，记录tag/字段名/wrapper不得免费。下一方案应分别定义wire token/depth/node和重建语义计数；以原字节数得到wire节点数≤wire bytes这类独立有限界，避免直接复用原1M而误拒。

还有一个精确byte外壳差额：0475限制的是 `len(canonical(payload))+len(canonical(rows))≤8,388,608`。若新恢复入口收整个execute_profile四键返回的canonical JSON，`jsonPayloadDigest`/`rowsDigest`各64个ASCII字符及四键/标点另占187B；标准库仅计算固定全null占位封套为195B，扣两个null的8B即187B。所以这个wire输入的完整成功上界是8,388,795B，而非原8MiB。可选择入口分接原payload/rows bytes及独立摘要，或另有严格B+187的wire域；这不放大原payload+rows门。原调用者未对整个返回调用 `_profile_json_bytes`，未来不能用这个8MiB函数直接编码完整返回然后宣称所有原成功都可保存。若另加新版本外壳，须再明确其固定字节域及费用。

ProfileValue须先将保存的domain/value/language解成严格的待比较原生形状，不直接构造ProfileValue。只由当前canonical parse_value(originalTermInput,None,R_parse)得到fresh值，再检查：I/S/L是精确str，B是exact bool，N是完整Number三个字段，Dz/Dl/Tz/Tl是完整Calendar及嵌套Number；domain和language也逐项核，不RDF等价化、不做值修复。全部相等才在ComparisonEvidence里使用fresh对象；任何末项差异原子失败。当前parse签发依赖私有weakref注册表，故必须持有fresh值强引用至全部API调用结束；pickle或同字段构造都不会恢复旧发行身份。

## 三、确实丢失或不能由保存JSON自证的东西

1. **原对象alias身份丢失。** 两个同字段SourceRecord/TermInput原来是否同一对象无法恢复。机制typed编码按每个出现的全部值收费、并不编码对象id；恢复可按完整字段相同进行intern/cache，不声称原对象关系得到了保留。缓存键必须含TermInput四字段、source是否None、SourceRecord四字段，并区分None/空串、raw language大小写、plain/xsd:string等，不只用RDF term key或lexical/value。缓存不能免重复occurrence扫描、T05编码或issuance费用；hash碰撞须完整键核对。
2. **发行身份丢失。** ProfileValue原id/weakref不能恢复；parse重发行可补当前机制身份，但不是正式producer授权。输入或保存record自报相同module名字也不是canonical class。
3. **原限额来源和原matched集合身份不自证。** JSON含实际L数值、defs/Catalog/matches，不含可信allocator凭据。需由独立可信原输入/分池上下文复算N≤100、按rule_id稳定divmod的所有额度与disabled/原输入顺序，再逐保存字段核对；跨child父进程的纯测试fixture绑定可验证此内部协议，但不冒T01生产授权。保存L/matches自身值相等不证明它来自原成功child。
4. **原图原文与sourceDigest前像不是普遍齐备。** 下面分域精确说明，不能笼统宣布两域均不可或均可恢复。
5. **原planDigest与aggregate图结论未由16c API核。** 16c只对给定child的fresh执行批次、保存typed payload/digest/profile及当前发行比较值核一致；没有返回fresh plan给调用方核planDigest，也没有重算RDFS、aggregate evidence/graphBudget/termSources。因此这些外层字段必须逐schema保存并用独立可信原payload摘要绑定，或明确只保未重算metadata；不得凭API字符串返回把所有外层内容称重新计算通过。不要为补planDigest偷偷额外compile而把费用藏进三池。

## 四、input/source摘要前像的精确分域

`_execute_profile`只在payload留inputDigest/inputDigestDomain/sourceDigest/definitionsDigest，未直接留original_bytes或单独source对象。definitions完整在reasoning里，可按原投影/JSON域重算definitionsDigest；这不是原saved-definition权限证明。

- `utf8-turtle`：当实际raw text≤65536且有捕获occurrence时，termSources中的SourceRecord通常携完整原text，可单独核UTF8(raw text)及inputDigest，且可按SourceRecord原值重算sourceDigest。text>65536时source.text明确None，不能从图/N3/termSources逆造quote、空白、注释、prefix、base或原字节。完全空图/无occurrence而caller给source_reference/revision时，源单对象也不必出现在reasoning里；不能普遍重算sourceDigest。若纯恢复只要求机制一致性，这不是阻断；若要求普遍验证原raw input/source摘要，就需另交可信原bytes/source binding。
- `profile-structured-records-json/1`：`profile_graph_from_records`逐record三个TermInput原顺序capture，termSources含全occurrence与ordinal，即使Graph对SPO去重也不删它们。严格核ordinal恰0..3n−1并按每三项分组后，可在不跑Graph/matcher的情况下复原原records的投影值，原Tuple→JSON array与原投影域一致；sourceDigest的原tuple也由这些source按序形成。因此该固定domain存在从已保存termSources重算inputDigest/sourceDigest的完整值路径。仍要绑定正确domain/version；不能对text域套该分组规则，也不把重算成功当producer认证。

最小选择是**不改0475 writer**：下一纯恢复入口要求外部trusted readback context持有原payload bytes摘要、rows摘要、实际implementation三字段、原ordered definitions/Catalog/disabled及可信allocator输入，另提供原input/source绑定或标明确认范围。纯测试父进程可在生产成功时独立捕获这些事实并绑定原fixture；这只是独立纯阶段验证载体，不是synthetic正式Job/Store/producer授权。需要普遍检查text原文时，该context另持原raw bytes及source四字段；原文缺失时不能无提示降级为“全摘要已核”。若未来正式落盘要求自包含raw前像，这才需要由T01/实际writer owner申请最小新增载体域，必须受独立byte/R/权限/窗口门，不能本轮直接添字段。

## 五、最小实现边界建议与未关闭事项

建议将未来pure decode/reissue/recheck收在一新私有模块 `packages/engine/src/ontolearn_engine/semantic_profile_restore.py`，新直接测试 `packages/engine/tests/test_semantic_profile_restore.py`（未来精确批准后才创建，绝非selected第六测试）。只读原字节采用16c的 `quality/rule_revalidation.py`，不改七机制/原预算/root export，不复制一套checker/比较器。无Store/worker/public route、无现0475载体delta；scope严格是bytes→有界严格结构→当前发行值→原childL批次一致性。模块不得为了补原matches重跑matcher，不得缓存或修复一个损坏的保存ProfileValue。

原8MiB JSON+rows与32语义层/1M语义nodes是成功输出条件，不是通用传输解码器已存在。还需主方案独立列出wire扫描/UTF8/重复键处理、schema访问/整数与hex字节解码、容器/record构造、完整键生成/碰撞或排序比较、每次occurrence扫描、raw/canonical/typed/hash摘要及原输入持有/复制的预算域；其中多数不是T05三池内成本。若使用普通hash map，不能只写平均O(1)而省掉最坏碰撞和共同前缀扫描；可用明确有界完整键比较/排序归并来给更可审计的费用来源。此盘点不证明R_work≤W或R_input≤I。

必要未来验证：真正独立child仅接JSON bytes与独立绑定context，无原内存batch/ProfileValue；全部false/true原matches、重复SPO多source、source40000、空source/None区分、disabled/实际空batch、所有最后字段篡改、Number负零/Calendar嵌套字段、错误tag/unknown键/duplicate键/inthex/byteshex、原limits污染/重试、pickle/alias/手造ProfileValue拒绝、整次R耗尽及最后child失败无前缀发布。source40000应先在实际I05入口成功再算此纯阶段见证，不借T05单机制旧成功代替该组合事实。

正式producer成功终态、项目/快照/作用域、source/定义/Catalog权限、读取和保存窗口/撤回GC仍由T01前置；selected、长期保存字段、公共协议、GUI、包和父门没有关闭。本件仅给静态表示/可实施边界意见。
