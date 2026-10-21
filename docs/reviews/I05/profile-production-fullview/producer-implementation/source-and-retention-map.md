# Producer 六文件作者交接与收费映射

此报告为作者提供的实现和证据说明，不是独立审查通过。六文件已停止源码写入，root 正接手另外三个 writer；报告及脚本仅在本过程前缀。完整交接字节见 `six-file-handoff-manifest.json`；所有新增显式循环/推导式原文和所在函数见 `new-loop-inventory.json`，避免只列 API 而漏内层工作。

## 已运行证据

- `01-pytest` 原始首失败：新 empty 夹具未声明 urn:unmatched Catalog property，实际原 compile 正确拒绝。只修新测试声明，未改旧输入/oracle。
- `02-ruff-check` 原始首静态失败保留，`03/04/07/08` 为明确逐次格式/修复记录，`05` 后续未使用 local/import 静态失败也保留。
- `06-pytest` 新专项 50 passed。覆盖实际单次 core/defs/catalog、compile 前同一 L 对象、旧 wire 对照、strict RuleSpec/consumer roundtrip、未知/重复键/数字/尾/Unicode、source 65536/65537、两层 Turtle UTF8、foreign type hooks、fake actual parser before-core 拒绝、五个 C 域实际所需上界与 -1、late failure 清局部、长 NUL+astral 在 encoder 前拒绝。
- `09-ruff-check` 六文件 exit0；`08-ruff-format` 无变化。
- `10-pytest-regression` 1024 passed / 27.05s，argv 精确列新两 tests 及原 integration/errors/source/limits/execution/restore/restore_limits。此时 root 尚未接手三 writer，不能当后续九文件最终同版结果。
- `11-producer83` 实际新 API：78 success / 4 原 ProfileExecutionFault / 1 原输入缺失未执行 / 0 MaterialFailure。原只读 probe 的 _load_inputs 校原 1839011B/SHA；直接复用 _construct_records，不读 expected 不补 repair 规则。每成功保 payload/rows/source/defs/catalog 摘要、原捕获 allocation 全字段及 C receipt；失败完整保 error/diagnostic。未比较独立数学 oracle，也未执行 Store/Job/worker/permission。
- 每次均另存 argv/cwd/UTC start/end/exit/timeout、完整 stdout/stderr。11 自身执行 hard timeout180s；原数学 probe 的 deadline 不因此变成产品默认容量。

## 数据合同与来源边界

`prepare_profile_material` 固定 text 原 UTF8 或有序 exact tuple[tuple[TermInput,TermInput,TermInput]]，source 为 Turtle 原 SourceRecord 或 structured 每个 term.source 的 occurrence tuple。None/空串/原 language_raw、顺序及 SourceRecord 四字段不归一化。raw RuleSpec 八字段、Triple 三位置、Comparison 三字段、Variable.name、TermInput 五字段只作固定类型语法投影；原 compile/profile parser 仍负责语义合法性及原机制细项长度，codec 不制造 PV、数字、matcher 或新的 canonical authority。rule_id/source identity 另有限长度门；body/编码总量各 8MiB、Turtle1MiB、规则100。disabled 原 tuple/原规则序保留，不从布尔权限位推授权。

D_rule 为 flat `profile-rule-definition/1`: rules 中每项 enabled + 原八字段；disabledRuleIds 独立保序；严格 decoder 固定 tag/keys/类型，禁数字/重复/未知 key，重编码逐字节核同 enabled/disabled 关系。raw definitions_preimage 仍为原 serializer 对原 rules tuple 的 wire，所以 D_rule wrapper 不冒充旧 raw defs 编码。

consumer U 分 assertedRecords/ontologyRecords，每层明确 inputDomain/input/parserIdentity；Turtle content 为原 bytes 的 exact hex 数据表示，原 UTF8 从未丢成截短 SourceRecord.text；structured 保存原 raw term/source occurrences。source 前像独立含两层 SourceRecord/occurrences，Turtle digest/text 按实际原 bytes 核同（超过65536B 的 text 必须 None）。两层可混型、可明确空；不依赖 K 或任何 producer 旧输入。

D_consumer 固定私有版本 `i05-consumer-definition/1`，只收实际既有 semantic_execution._request:153–166 使用的 query `{text,references?}` 或 constraint `{turtle,enabled,references?}`；references 原 `{layer,id}` 序列，不填默认 enabled/references。不存在执行 query/SHACL，也不声称新 wrapper 是 T01 确认/Store canonical。consumer parserIdentity 只是上游提交的原数据，待真实 T01 owner 认证。producer 的 parser_identity 则必须匹配当前 domain 对应原函数名 + i05-finite-7 固定 tuple，不能 caller fake/v999 成功冒充实际 parser；完整代码身份/锁/安装供方仍由未来 T01/T03 供应。

## 唯一计算发生点

semantic.py 原 _profile_reason 仍唯一 matcher body；_profile_definitions return 后留实际 ordered `(ordinal,spec)` tuple，disabled 完成原校验后留原 tuple，_profile_catalog return 后留实际 Catalog。每个原 ProfileLimits 创建后、Budget/compile 前 capture.allocation 留同一对象；没有另一次 divmod，没从 mechanismBatches/JSON 反推 limits。

semantic_execution._execute_profile 保唯一原 preflight/parser/reason/projection/rows/error adapter。生产入口只选择 exact private _ProductionCapture，原 facade 仍调 semantic.reason；production 用同 core 私有 wrapper，一次计算。完成时捕获原 encoded/source_encoded/defs_encoded/rows_encoded 和原四键 wire；全部成功后才发布 frozen ProfileComputation。catalog_json 对实际 Catalog 单次额外投影，付 stage8，不反解 saved payload。

实际新 tests 对 _profile_reason/_profile_definitions/_profile_catalog/compile/evaluate 使用 wraps 观察实际调用，没有提供替身 result/expected。pure restore 测试 expected 从成功实际 capture 字段构成；不是拿 restore 旧 payload 生成 producer 输入。

## C 八阶段与普通委托

M=8388608；A=Q+D+3M≤6M，N=max(1,rules数)≤100；consumer N=0。固定 traversal128A+65536N、scan_copy64A+65536N、hash16A+65536N、scalar16A+131072N、objects8A+2048N+4096。overrides 只能 min 降低；一个 ledger 只能 begin 一次。prepare 的 Q/D0 使用较保守 A=3M，production 新独立 actor ledger 则先从 exact bytes 长度固定实际 Q/D，同一调用从 stage1 连到8，不 reset。每 stage 只 enter 一次，traversal 累计≤16J；未使用 stage 记0，没偷第九遍。

| stage | 实际入口和工作 | 先票/保留 |
|---|---|---|
|1 input|_prepare_profile_material:674；consumer _prepare_selected_material:895；strict decode 可 _read_syntax_json:510|原 text `_text` 后再原 UTF8，structured `_records` 后 `_encode`；consumer 两层身份/UTF8/hex/records。J=M。|
|2 source|原SourceRecord构造/structured occurrence tuple；consumer严格source decode/实际digest/text核同|source `_encode`；hash按实际 bytes、tuple3n对象与4n traversal。J=M。|
|3 definitions|_definitions:454；decode_rule_definitions:621；consumer actual typed D|原raw规则和flat D各一次 `_encode`，未知动态schema拒绝。J=M。|
|4 preimage|production:182–197；consumer decode:956|四对bytes length合计先 scan_copy 再比较；native source再 `_encode` 后逐bytes核同。J=3M。|
|5 actual compute/capture|production:198；capture before_input/definitions/context/catalog/allocation|仅原 core 执行；新增L/slot每项40 traversal/24对象/1024scalar，在 CapturedSlot 前。defs/context/catalog只留实际引用，按实际项数新增槽/对象先付。J=3M。|
|6 original projection|capture.before_projection:98|原 projection/原三份encoded/payload同时留存之前一次付 traversal16M、scan_copy32M、scalar24M、objects8M。不声称内部有逐allocate hook。J=3M。|
|7 rows/hash|capture.before_rows:108|原payload UTF8 decode、切rows、rows编码及全部相关hash之前 traversal16M、scan_copy24M、hash4M、scalar8M、objects2M。J=3M。|
|8 publish|production:207；prepare/decode收据|captured slots ->OriginalAllocation 的两个推导式先8slots+4rules+8 traversal、6slots+6rules+16对象；Catalog普通投影前8M traversal/16M scan/8M scalar/2M objects；hash按实bytes。receipt先64 traversal/64对象/1024scalar。J=3M（仅数据prepare为M）。|

### 新循环/委托逐函数映射

- CaptureLedger init/begin 固定≤5 overrides、3参数、5个domains；bootstrap64对象覆盖有限控制容器，公式计算不依赖输入对象方法。所有 domain 名必须 exact str 再 membership；int/bool严格分开。debit/reserve 为实际工作/并持先拒；failed 不减累计或伪造live0。
- `_text:250` exact str 后才 len/UTF8；2*(4len)+1 scan_copy 和4len scalar先于 encode，finally丢临时bytes再退票。新 escape 预扫先 len+1 traversal/4len+1 scan，逐字符算标准JSON转义UTF8上界，超过M在 encoder前拒。最大合法单chunk UTF8≤M，即便一astral使 PEP393整体4字节宽，chunk storage≤4M，原6M ordinary票覆盖；长NUL+astral测试通过。最后4len是保留source primitive引用的保守预留。
- `_project:296` 每节点先1 traversal；list/tuple先len traversal和len+1对象，再递归。dict先exact key类型/长度，再n² traversal+(n+1)*key_width scan+key_width hash，覆盖最坏hash碰撞/排序；2n+1对象先于新dict，key/value再递归。六 raw class固定扫描，字段读前2f traversal/2f+3对象；RuleSpec tuple成员all先len traversal；foreign对象不调用 len/iter/hash/equality。
- `_encode:385` safe projection先票逐节点；委托前2M traversal/8M scan、6M scalar/M+64对象覆盖普通encoder escaping/stack；chunk获得后先8len scalar与UTF8 scan，再encode与append；先reserve实际data长度再append；最终bytes前再reserve len(output)，双buffer同时有票。finally清safe/output/encoder/chunk/data后，仅退真实内部临时票差，成功bytes继续有票。总输出>M有限失败，不截尾。
- `_hash:427` exact bytes 后先实际len hash、128scalar/1对象，再 sha256/hexdigest；返回digest继续留票。
- `_records:435` exact tuple/≤100000 后先4n+1 traversal，内部每row exact tuple3、三个 exact TermInput；不解析数值。`_identity:445` 两字段固定3 traversal，字符串另 `_text`。
- `_definitions:454` 原rules≤100；ids比较每项len(ids)+3 traversal和2*(lenids+1)*(lenid+1) scan前付，disabled序/重复亦按lenids+pos付；body每项len(disabled)+10 traversal/24对象在成员比较/append前。rule raw/D两编码各自收费，未从json反推原规则。
- `_read_syntax_json:510` decoder前8B+1scan/4B+1traversal/12Bscalar/8B+64objects，首遍quoted/escaped depth≤32后才fixed json.loads；固定number函数拒所有数字。pairs固定key白名单、每object≤白名单长度，48n+1 traversal/1024n+1scan/2n+1objects在新dict前覆盖重复/未知key核与固定hash。UTF8/JSON树普通委托采用整体先界，无importtag/caller hook。
- `_syntax_native:599` 每节点1 traversal；list先len traversal/2len+2对象；六个fixed class字段先2f traversal/2f+2objects再构造，最终raw `_project`再次核位置类型。decode_rule_definitions各body32 traversal与2f+4对象再RuleSpec；enabled一致性先disabled长度+1 traversal。最后actual/canonical bytes合长度scan前付，才逐bytes比较。
- `_consumer_definition:797` fixed3 keys前8n+1 traversal；references≤100000、每ref必须exact dict2且固定layer/id，先8r traversal，再由 `_encode`对子字符串/最坏hash/JSON付费。未补不存在的数据。
- `_selected_layer:826` shorthand tuple包装前对象1；Turtle decode前8B+1scan、4B scalar，实际丢临时text后退4B；输入原byteshex由 `_project`另4B+32scan/8Bscalar/5对象覆盖。
- `_selected_source:850` Turtle四字段 `_text`、hash实B，source.text≤65536B时decode前8B+1scan/4Bscalar；text equality前8B+1scan。不把长原文截成来源缺失。structured source生成先4n traversal/3n+1对象。
- `_layer_from_json:873` fixed3 keys，8traversal/3对象；hex≤2MiB字符，fromhex前4len+1scan/lenscalar，然后strictUTF8门；structured只固定rawnative decoder。outer consumer比较最多3对完整bytes，分别合长度+1scan在比较前付；retained原生/编码scalar4Σbytes、objects2Σbytes+8后再frozen发布。
- production四个preimage固定type门只读 caller持有bytes；_same_bytes:136 先合长度+1scan。capture defs/context/catalog按真实项数留ref；allocated L原对象只计新slot，不重新构造L。allocation与Catalog委托上述stage8。drop只解本capture引用，不声称接收者引用消失。

## 真持有与异常

成功 material/source/rules/source occurrence、actual definitions/catalog、native_result、wire(payload/rows)、五组实际encoded bytes、allocation、receipt 同时可达；返回record和receipt明确 receiving caller 负责持有。receipt retained/peaks是**保守预留逻辑单位**，不是精确Python对象大小、CPU或RSS；ordinary整块有意预留超过当前实际占用。prepared material caller持有的原前像，在production新actor账不冒充跨actor释放。

public execute_admitted_profile_job 捕获错误后新建有限 MaterialFailure/ProfileExecutionFault，退出except/finally后才raise，原context链消失。finally capture.drop；checked/catalog_json/allocation/receipt/encoded_source/循环value/actual/supplied/reference/revision逐一None；失败outcome None。原 private execution/helper错误frame只在被丢弃原exc链里，不附新publicerror。caller输入material/error_catalog/schema仍caller所有，不能假称抹除。五domain -1测试含late failure，检查public生产frame所有新大locals为None、context None。decode/prepare public链同样清树/bytes/native新locals后再raise。

## 独审必须单列的边界

1. 固定 bootstrap控制容器和若干很小的列表/tuple在进入下一条reserve语句前分配（如ledger.begin初建计数dict、_definitions的ids=[]、capture.__init__的slots=[]）。它们在固定bootstrap64对象/上阶段retained+8的保守控制额度内，但代码没有逐分配前hook；若独审要求“每个控制对象也必须在其自身第一条reserve之前显式票”，需按此精确位置改序，不能把本报告当已证明所有Python分配hook。
2. stage6/7/8 ordinary projection/JSON delegate采用固定整块先票及原_ ProfileProjection的1,000,000nodes/8MiB估算/depth32门，不是新库内部仪表。最坏碰撞只对本codec构造的任意dict显式n²预付；原native投影dict为原固定schema，其动态内容为有序tuple，不得把这一证明外推到任意用户dict或未实现selected Graph。
3. 原 profile 细项（term16KiB/source64KiB/when等）仍由原parser/compile付原机制账并保错误分类；rawcodec只作类型/总门，不等价一次机制验证。83保持原四资源失败支持兼容，不能据此声称所有恶意raw语法都已形式证明。
4. 本次没有真实T01 admission/Store/worker/资源actor监督，没有producerCodeManifestRef可信供方，也没有fullview三writer最终同版证据；root后续正常check及独立源码/生命周期审查仍必需。
