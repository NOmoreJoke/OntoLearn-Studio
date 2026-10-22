# 有限 UTC date 独立静态验收与 oracle 计划

2026-10-22。计划可供唯一 writer 编写新测试；**这不是产品验收通过，全部运行项目仍待真实候选。** 本作者只新增本文件，不改源码、测试、旧 C 原件或过程，不创建树/Goal，不执行产品、第三方库、pytest、GUI 或外部审查。本文不替代指定双外审。

## 输入身份与职责

精确树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-shacl-date-policy`，分支 `feature/weekly-i05-shacl-date-policy`，起点/读取时 HEAD `65e31d331b315c245e1f921c3558bb7886adbd27`，批准 develop base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。root 唯一维护 semantic.py 与新 date 测试；读取期间 semantic.py 已出现 owner WIP，本文使用固定设计及固定旧源码解释边界，不采用 WIP 的 actual 输出建立预期。

全文读仓库外 `iteration-control/2026-10-21-weekly-release/I05-shacl-date-policy-source-window.md`、fixed-inputs.json 及固定设计。fixed-inputs 为56515B，SHA256 `ad3219884b4efa761784dca8e42c0d1eb53f411abd529b1c86b9bd4ef0269506`，已完整解析其145成员、唯一既有 writer/144只读及唯一新测试146受控安排；不声称本作者逐145运行或审完全部源码。设计22938B，SHA `1457aea0ba8b15ed0d137492dd648bc846e9757e067cf2cf506b70949aa996cc`，current 与固定 Git 精确相等。完整读 inputs 中 user-AGENTS、operating-AGENTS、developer-common 原件，SHA 分别 `a9d68cf19ce966ce7df8854d5e1fc6757fc9ddc899ab7595bbcd2777b1652932`、`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、`e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`。本次精确只读/单文档任务优先于历史新建 Goal 或默认运行命令。

只读 C 输入8505B SHA `eeab821ccd71d55eed425a08b34d07648e623c0aa34eb2eabf66b839bbb426f6`，goldens8163B SHA `c25e7afcc593a7be09fc8b2ca29af9cff28a7a1e030a13b98aa5e7d88d596440`，均逐字等65e Git。读固定 semantic.py 的 terms、shape、validate/check/report 路径及旧整数入口测试，参考 PRD FR-500/503/504、附录 C/D 的真实报告、明确范围及输入版本边界。旧 goldens 中 currentEntryGap/pending 是历史，不改写为当前能力。

## 优先处理的实际冲突与实施风险

1. **旧回归存在确定冲突。** 固定 `packages/engine/tests/test_semantic_shacl_entry.py:300` 把 `{data_policy:WIDE, range_policy:"utc-date-range-v1"}` 列入未知策略；L306–308 对 `validate_shacl_text(None,None,**options)` 固定要求 `SCOPE_SELECTION_TYPE_INVALID`。新设计§1已使该 policy 合法，§3要求继续文本类型门，应为 `TEXT_TYPE_INVALID`。旧测试只读、正常 check 含旧测试、新设计不特判非法文本，这三条不能同时满足。已报 root；root 已请求总控只将该未知参数 v1 改为仍未知 v2 的精确返还，尚未获返还前不改。本文不授权该修改，不能删测试、skip、改新 oracle、宽接两码或故意对 None 特判取绿。
2. **总费用 oracle 必须先独立冻结。** §5.1每项单位及 collector 小计可精算，但完整 discovery 查询次数、计划成员/关联引用的层次与重复引用读取次数需要实现前明确的操作清单。不同合法查询拆分会改变总票。不能在 actual 成功后把其 usage 当既有数学预期，更不能只证明 `used <= 1M` 就签全部访问先付。root 已确认采用下述 collector invoice，并将公开1M真实图、D1、私有少一票分开；实际明细仍待固定候选逐项核验。
3. **固定库兼容性仍待真实证明。** 自身 Gregorian/原词法门通过不证明真实 Validator 对0001/9999或报告保留原 spelling。若固定库的精确 date/年月日门失败，按设计是 `VALIDATION_FAILED`/Validator0；需保留具体反例交 owner 窄修，不缩域、转时区或造 violation。未运行库，本文不预报这些极值已成功。
4. **混合两侧不能机械断言同一阶段。** date bound 配非date value 在比较门拒绝；反向 string/lang/IRI bound 本来不在通用 inclusive 参数域，会先 `INVALID_SHAPE`。反向 integer/dateTime bound 才能进入 value 的 `RDF_TERM_INVALID`。shape 的坏 integer 无论 data_policy 都在 parse-shapes 拒绝。
5. **D1 的两个结果必须分开。** 同一 RDF 的次序变化应保持新 preflight 的费用、首错误和失败操作一致；将错误放最早/最晚稳定路径则是两个不同输入，不能要求都报域错误。下面给出独立费用下界，防止隐藏资源优先级。

## 一、真实报告的统一 oracle

所有新成功样例必须直接调用 `validate_shacl_text`，两 keyword 都显式指定。仅 observer 委托真实 `Validator.run`，先调用原 method，再保存实际 conforms、原始 report RDF 与原 data graph；不供应 report/conforms、日期替身、规则 comparator、预制 Graph 或全局库 monkeypatch。预期只在调用返回之后参与断言。

外层必须恰四键：entryVersion/dataPolicy/rangePolicy/report；UTC是 `i05-shacl-text-2`，legacy是 `i05-shacl-text-1`；strict 与 integer宽策略分别保留身份。报告恰实际 `conforms` 与完整 violations，不能用数量、component 集合或裁掉 value 代替。约定纯输入命名为 `urn:date:s`、path `urn:date:p`、NodeShape `urn:date:n`、PropertyShape `urn:date:ps`、target `urn:date:C`。

下文 `V(component,lexical)` 完整代表一行：focus=`<urn:date:s>`；path=`<urn:date:p>`；constraint=`<http://www.w3.org/ns/shacl#COMPONENT>`；sourceShape=`<urn:date:ps>`；value=`"原lexical"^^<http://www.w3.org/2001/XMLSchema#date>`；severity=`<http://www.w3.org/ns/shacl#Violation>`。测试必须展开六字段，原始 report 用结构对应核 BNode，不固定随机 BNode ID。两违规按既有报告稳定顺序比较完整集合；optional value 只有原报告实际缺失时为 None，不制造假节点。

原 `C-inclusive-date-entry` 不改：`urn:m1:s` 的 date与 min bound同为 `2000-01-01Z`。UTC对应原 golden 已存在的 `ifI05ExplicitlySupportsXsdDateOperatorExtension` 条件分支：Validator1、true、空违规；legacy仍 Validator0/INVALID_SHAPE。不得把 coreOnlyExpectedReport 的 false 误用于已采用扩展，也不改旧 pending。

## 二、必要的纯输入与完整结果

每个基础形状都是 named NodeShape→named PropertyShape、直接IRI path；每个数据样例有实际 `s rdf:type C`。没有隐式 ontology 或规则推理。

| 组 | 具体输入/变体 | 独立预期 |
| --- | --- | --- |
| min三点 | bound=`2000-01-02Z`，value依次01/02/03日 | false+[V(MinInclusiveConstraintComponent,2000-01-01Z)]；true/[]；true/[]，各Validator1 |
| max三点 | 同bound，value依次01/02/03日 | true/[]；true/[]；false+[V(MaxInclusiveConstraintComponent,2000-01-03Z)]，各Validator1 |
| 两界正常 | min01、max03，三个值01/02/03 | true/[]；各值/每个约束都实际检查，不以一次检查缓存代替费用 |
| 两界反向 | min03、max01，value02 | false，完整 min与max两行同value02；bound不交换、不预造shape错误 |
| 反向无目标/无值 | 上一shape但没有C focus，或focus无p | Validator1、true/[]；若另有minCount1，则是下述真实计数报告 |
| 公历可取域 | 0001-01-01Z、9999-12-31Z、2000-02-29Z、1900-02-28Z、2004-02-29Z、2100-02-28Z，分别在bound/value两侧使用相等合法对 | Validator1、true/[]；极值实测兼容才算通过 |
| 公历拒绝 | 1900-02-29Z、2100-02-29Z、2000-02-30Z、2000-00-01Z、2000-13-01Z、2000-01-00Z、2000-04-31Z、0000-01-01Z | bound/value各侧分别固定前门；原terms已判illtyped时 INVALID_LITERAL_LEXICAL，不到新域/Validator |
| spelling拒绝 | 负年、10000年、三位年、单数月日、小写z、首尾空白、全角数字、内嵌T、无TZ、+00:00、非零offset | 两侧独立；通过原terms但越新域的bound为INVALID_SHAPE、实际value为RDF_TERM_INVALID；原terms先拒的具体输入单独固定parse阶段 |
| 多值普通违规 | min02，实际values01与03 | Validator1、false且恰01一行完整min违规；03保留在实际data中，不删除非违规值 |
| 多值域失败 | 合法Z与合法非Z date两个value，交换文本顺序；再加IRI/字符串混合 | 整次Validator0/相应前门；不能先发布合法值的报告或过滤坏值 |
| 无值+必填 | 合法date bound与minCount1，s a C但无p | Validator1、false，完整MinCount行：同focus/path/source/severity，value=None；无虚构date范围行 |
| 不相干date | 非focus主体的同p，或focus的另一个非range路径含合法非Z date，实际date比较值为合法Z | Validator1、true/[]，不新增全图Z门；原terms原本拒的坏date仍不能绕过 |
| 共享property | nA→targetCA、nB→targetCB，共用ps/p；sA/sB实际各自类型，另有非target主体同p非Z | 两个关联的实际target都检查，非target不检查；nB的坏值不能因ps已见而跳过；真实报告只对应实际focus |
| 同focus双类型/重复关联 | s兼具CA/CB，两个NodeShape共用ps；同一date值重复参与 | 新preflight重复关联读取/检查均付费；报告以真实Validator为准，不能按preflight次数制造重复报告 |

spelling/坏公历的逐字输入不能用一个宽泛“允许 parse 或新域任一码”断言掩盖阶段漂移。测试作者应在固定库源码/首次真实原件中固定其原terms ill_typed事实并标明阶段；未定项留待核，不从候选最终输出反填数学日期预期。

## 三、bound/data 混合两侧及阶段优先级

以合法date `2000-01-01Z` 为一侧，另一侧分别用有效 integer1/decimal1/float1、dateTime `2000-01-01T00:00:00Z`、plain string、language string、IRI。date bound→这些value：只要原terms通过，实际date pair 必 `RDF_TERM_INVALID`/Validator0。非date bound→date value：合法数值/dateTime bound进入pair门同样拒绝；string/lang/IRI bound在通用shape门 `INVALID_SHAPE`/Validator0。均不能把库排序结果当普通inclusive violation。

同一property shape 的 min为date、max为integer，及 min为integer、max为date，两种都在 bound阶段 INVALID_SHAPE；即使无focus、无value也不能绕过。不同property的一条date约束与另一条普通数值约束不因此混为同一操作数域。

strict 下 bad xsd:integer data仍 INVALID_LITERAL_LEXICAL；宽策略只允许 data对象的该精确datatype进入：无date范围时沿原C得到真实Datatype false完整一行；date bound遇它则 RDF_TERM_INVALID/Validator0。shape bound的坏integer在两策略都 INVALID_LITERAL_LEXICAL。

必须有交叉错误样例：

- 未知policy+坏文本：先 SCOPE_SELECTION_TYPE_INVALID；合法policy+None：TEXT_TYPE_INVALID；遗漏任一必填keyword：TypeError。不得因新政策扩展弱化exact str门。
- shape合法但date bound非Z，同时data含scope公理：bound INVALID_SHAPE先于FACT_SCOPE_CONTAINS_AXIOMS。
- bound合法而实际value非Z，同时data含scope公理：FACT_SCOPE_CONTAINS_AXIOMS先于value域门。
- bound合法词法但库值兼容失败：VALIDATION_FAILED、Validator0，先于scope；value库兼容失败只在对应实际value位置发生。
- 单collection含早排域错与大量其他成员：必须先完整付费收集/构键/排序。若收集即缺票则GRAPH_INPUT_LIMIT，不可边枚举边先报域错。
- 同一property min/max检查始终min先；多个property/NodeShape/targets/values均按§5.1固定键。多种输入错的优先级只对已进入新阶段作上述承诺，不能把旧通用结构门的集合枚举顺序伪称也已重定义。

## 四、D1稳定次序与1M费用 oracle

以下只讨论新 `i05-utc-date-preflight/1` 固定政策work，不代表CPU、native内存、whole-H、解析或整个Validator费用。

对无额外去重的n成员集合，独立collector invoice为：查询迭代器1；next n+1；保留n；构键n；排序预约 `1+n*ceil(log2(max(2,n)))`。总计 `C(n)=3+3n+n*ceil(log2(max(2,n)))`。例如 C(0)=3、C(1)=7、C(2)=11、C(3)=18、C(20000)=360003。有序引用读取及缓存查找另计，不藏进C。n=2^k±1另列排序票，`ceil`用整数边界，不以浮点log或真实sort比较次数取代。

正式预算验收至少分三种证据：

1. **公开固定cap的真实图。** 选在原每文本1MiB/每图100000界内的纯输入，按设计冻结完整手工操作清单与费用算式，构造总需恰1000000的成功图。成功仍须真实Validator1及完整报告；公开追加一个focus等超界图必须先付拒绝、Validator0、无部分报告。少一票可在完全同输入的私有lower-only余额999999注入中核验，明确它不是公开可调cap。若公开输入可实现票数是离散格，不能把999999或某个测得usage冒充1000000恰界；须给出算术构造或具体不可达证明和最小验收修订，不暗改cap。
2. **私有计费原语的exact/差一。** 用真实ledger/debit，不供报告或复刻preflight。余额1000000，先付999999、再1后应恰0可结束；再需1必须在相应操作/append/next前拒绝。另对排序预约、7项date检查逐项与库门1票作少一票故障。可用测试私有窄缝降低剩余余额，但明确仅是故障注入，不能当公开真实1M图证据，不能对caller新增可调高cap入口。
3. **真实逐动作 observer。** observer只委托原debit/query/next/append/check原发生点，不供应结果或票；按固定input手工invoice比实际记录，核所有next含StopIteration、空collection排序票、缓存命中/未命中、重复关联、逐operand无跨值date结果缓存。最后一票失败时对应操作marker为0，后续Validator为0。费用不能只用actual baseline回填expected。

公共恰界的条件算术复核：root 提出单NodeShape/单property/minInclusive合法UTC bound的计划建设24票、property/bound30票、值阶段固定16票（含focus集合常数3）；合计固定70。n≥32769时focus排序k=16，每个空path focus成本23，所以基础 `70+23n`。一个focus有m个互异date值时相对空collection增量为 `m*(22+ceil(log2(max(2,m))))`：每值新保留/键/排序3+k票，读取value/bound与分类3票，双侧date各8票。

原提案 n43470加2值/3值把2值误算48票；按上述公式它应46，故总费999998，不是1M。独立可行算术解为 **n43460，两个focus分别6值与8值**：k6=k8=3，增量150与200，`70+23*43460+150+200 = 1000000`。min bound用2000-01-01Z；每focus分别使用01日之后的6/8个不同日，防止RDF term去重。全部合法且应真实true/空报告。同图追加一个空path focus会需1000023票，公开cap应拒绝；不能把它称恰少一票。

此解只核算 root 声明的原子成本公式，尚未签24/30/16的完整操作invoice；必须把这三块逐项查询/next/保留/引用/排序/检查清单先固定，并用真实observer核对。若块内另有访问漏票或多票，先报具体差异，不能改公式/测试去凑恰界。对同一恰界图私有构造meter余额999999，仍委托完整真实路径，才是明确的差一票注入；公共默认仍固定1M。

D1纯输入定义：100个named NodeShape `urn:date:n000`…`n099`，同targetClass `urn:date:C`；各连独立PropertyShape ps000…ps099/path p000…p099，每个minInclusive均为合法 `2000-01-01Z`。数据为20000个named focus `urn:date:f00000`…f19999 的显式rdf:type C，额外只有一条 `(f00000,pNNN,"2000-01-01"^^xsd:date)`。约20001 data triples、600 shape triples；用紧凑prefix文本，两个文本各自必须实际核字节≤1MiB，不把空间展开到target×property×value。

- **D1-LATE**：NNN=099。第一份focus缓存完整收费360003；即使忽略其他一切票，前99个关联至少读取 `99*20000=1980000` 个focus引用，已超cap。因此到p099坏值之前必GRAPH_INPUT_LIMIT/Validator0。费用应同一最大成功前缀、同一失败操作位置；不得继续查找更“具体”域错。
- **D1-EARLY**：NNN=000。缓存仍必须先完整收集并排序20000focus；之后最早focus/最早path值触发RDF_TERM_INVALID/Validator0。需用冻结计划费用上界证明到该位置总费<1M，不能仅凭“错误排最前”忽略排序预约。若实现额外提前耗满，需指出多出的合法收费或不合约扫描，不能改expected迁就。
- 每组分别至少原序、逆序、固定置换三种相同RDF序列化/插入顺序；同组RDF term集合精确相同，保留实际输入摘要及解析后结构对应证据。比较错误码、实际失败阶段/操作、已付费用；不用 wall time 作为确定性oracle。
- 再有一个小的两value竞争反例与collection缺票反例，覆盖value排序键IRI先、Literal按datatype/language/原lexical，不用n3/date解析排序。D1大图不能替代这两个可手工审核的局部优先级例子。

## 五、旧分支隔离和原拒绝

strict/宽integer × legacy/UTC四组合各覆盖：原C date；原bad integer Datatype；普通整数inclusive；非date string-vs-integer普通MinInclusive违规；原dateTime equal/before；原term-identity计数/允许值。UTC非date范围不改普通SHACL类型错误为输入拒绝。旧C query两格保持原查询结果和规则精确比较区别，不把date测试当query重验或T05正式消费。

UTC成功和失败后，后续旧parse/query/reason/check、legacy date bound拒绝、strict badinteger拒绝均保持；无进程全局date转换/比较/DAWG/parser/logger/constraint map修改。SEMANTICS_VERSION/profile/规范pin不随组件entryVersion更换。一次调用的focus缓存不得跨调用复用；第二次改变target/value必须重新真实检查。

以下仍是实际前门拒绝且Validator0：未知/错误类型policy、坏Unicode/Turtle/文本类型/1MiB上界、graph100000超界、外联、data blank node、unknown datatype、nonfinite、IRI不合法、缺/重复target/path、不支持inverse/复杂path、无NodeShape、exclusive/任意SHACL。沿既有精确错误码表，不新建公共目录；不能以资源图或非法shape绕过来凑1M证据。shape合法但无target则仍真Validator1/true空，不因“没有工作”跳过真实调用。

## 六、候选交付时的静态与真实证据门

固定146来源前后身份，最小产品diff仅已授writer与新测试；旧只读测试返还若生效须另绑定精确来源，不口头扩大清单。一次必要正常check承载新测试、旧整数、77DAG/26shape回归，另核12sources；首失败原件留存，不重复不变专项。本文不运行这些命令或npx库；文档格式可由owner在正常静态检查时核验。

每次真实run独占环境/cache/basetemp/evidence目录，保argv、cwd、有限环境、起止、双流、退出/超时、完整输入身份、候选146前后hash。报告oracle逐样例预先固定完整六字段与conforms；observer保存实际原RDF而非重新拼接。资源/域错误只存有限码/位置/费用/调用计数，不发布成功部分report。先有真实候选与可追溯运行，后独立审新源码/费用/实际结果；此计划不将已采date政策扩大为正式execution/Store/Job/selected、whole-worker对象证明、SQLite保护解除或指定双外审/CI/平台/真人/合并通过。
