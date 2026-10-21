# f677 独立实际源码预算与持有审查

结论：**不通过，待两条前票问题修复后做 delta**。这是实际实现审查；不是旧方案、实现者自审或指定双模型审查的替代。未修改产品、其他报告、环境、分支或索引。

固定产品 `f677d8a3a642ef7ac7bf389218d43564762bcd9a`；adoption `e4460763890cf9550f359395df83260d75fe2e0a`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration`。逐文件身份及过程输入 bytes/SHA 见 `inputs.json`。独立核实139项 current=固定Git=清单 bytes/SHA，130只读项逐字等 adoption，adoption→产品实际仅9 writer。没有用数量相同替代逐字核验。

## 范围与方法

全文读取 latest-AGENTS/common raw、9754B根实施授权 raw，以及实现者 source-and-retention-map.md、new-loop-inventory.json。全文审阅新增 input.py 1021行、production.py259行、两新增测试；逐 hunk 审查其余五个 writer（semantic.py、semantic_execution.py、restore.py及两旧测试），并读取实际委托 `_ProfileProjection`/`_profile_json_bytes`、native decoder与 RestoreLedger 的有关上下文。readonly130仅做身份核验，不冒称逐行重新审计其全部实现。独立 AST 枚举新模块及 freeze/只读索引中的50个循环/推导式，原件见 actual-loop-inventory.json；没有将作者清单当作完整性证明。

本轮实际运行自有 probe.py.raw，并运行本树 `.venv/bin/python -B -m pytest -q -p no:cacheprovider ... -k fullview`：**43 passed,145 deselected,exit0,6.96s**。完整 argv/cwd/时间/双流/退出/无超时见 probe-run.json、fullview-run.json及各 raw。探针只观察真实函数或受控故障，不供应 matcher/计算结果；原件为 .py.raw，未把诊断脚本加入产品 lint 范围。没有运行全238专项、全仓check、生产Job、网络、GUI、包、SQL、worker、模型或真实OOM；root/实现者的结果只作他方报告，不记作本轮独立运行。

## BR-F01：P1，hash 在委托之后才预扣，开放

位置：semantic_execution.py:724–728 构建 payload 的三次 `sha256(original_bytes/source_encoded/defs_encoded)`；semantic_profile_production.py:98–114。stage6 before_projection 仅扣 traversal/scan_copy并留 scalar/objects；hash 的4M块在 stage7 before_rows:112才扣。

精确反例：实际 `prepare_profile_material(turtle(), (rule(),))` 后调用实际 `execute_admitted_profile_job`。将新 ledger 的 hash 下限设为674，正好等于前三阶段已付 hash。真实 stage6 仍依次 hash270/426/1036B，三次调用前 `used.hash=cap.hash=674`；直到 stage7扣4M才 MATERIAL_LIMIT/hash。原件 probe.stdout.raw 第一行保留成功对照及低限首失败。错误context为空、状态failed，不能撤销已发生的三次委托。stage1/2/3的674不是这三个新增摘要的票据；总量 cap很大也不能使事后收费合法。

最小修复：不增 cap，将现4M hash块整体移到 before_projection、任何这三次摘要之前；它可保守覆盖 input+source≤2M、defs≤M、payload+rows≤M的五次摘要。也可分3M和M，但须把对应预留分别放在委托前，并核实际 hash 路径。stage8 Catalog `_hash` 自行按真实长度先扣，不混入这4M。

## BR-F02：P2，固定控制容器 bootstrap 先分配后留票，开放

位置 input.py:74–89 `checked=[]`、append/tuple；begin:101–119创建 caps、used/live/peaks三个dict和两stage list后才 reserve(objects,64)；_definitions:457先 `ids=[]` 后 reserve；production.py:59先 slots=[]，:63后reserve4。

精确反例：`CaptureLedger(overrides=(("objects",0),))`，实际 prepare_profile_material。观察第一次 reserve64入口：六个控制容器均已创建，objects live仍0，随后才 MATERIAL_LIMIT/objects/stage0；完整记录 probe.stdout.raw 第二行。前置构造的 checked 及 slots/ids均可静态确认。它们有固定上限，未证实可借此形成无界内存或CPU放大；本条分级针对根授权“所有新循环/record/大encoder真实预付”的严格前票合同，不能以固定小量或后补票关闭。

建议修序：__init__保留已验证的exact tuple，不经checked列表复制；固定≤5项和重复检查必须明确归入控制bootstrap，不宣称数据遍历已收费。begin先用exact Q/D/N与已验证overrides计算对象有效下限，在任何新计数字典/list创建前检查至少64、声明64控制票；之后一次初始化live.objects/peaks.objects=64，不能先创建容器再调用reserve补票。state先进入运行/失败不可复用的语义应保持。_definitions与capture分别把其现有reserve移动到ids/slots builder创建前。不要扩默认cap或把旧W/I/O当作C的前票。

## C实际逐操作、阶段与持有映射

默认 A=Q+D+3M；production实际Q=input+source≤2M、D≤M，所以A≤6M；独立prepare/consumer以A=3M起步是更紧保守cap，并非凭后来真实长度扩池。N来自exact rules槽，production max(1,len(rules))≤100；consumer只在C取N0，不把0送入R或16c。五域公式与根授权一致；overrides只降、不重置；enter每stage只准一次，traversal在全局cap和该stage16J两处先扣。八stage为1输入、2来源、3定义、4前像比对、5真实捕获、6原投影、7rows、8发布。prepare不使用的stage保持0，不能重复借相同stage额度。

下表覆盖50个 AST 循环/推导式的所属函数及其费用来源；同函数多个循环合并说明，确切行均在独立清单。固定bootstrap例外按BR-F02处理，hash时序例外按BR-F01处理。

|实际函数/位置|前门、费用及并持|
|---|---|
|input __init__/begin 78/84/97/109|exact tuple≤5、pair2、exact域名/int且非bool；固定重复比较。初始化费用现为后扣，BR-F02。|
|_text250–293|exact str先于len；UTF8前2*(4len)+1 scan与4len临时scalar，finally先data=None再release；逃逸扫描前len+1 traversal/4len+1 scan。逐字符算 escaped UTF8≤M，禁止先制造超大chunk；返回原str另留4len，不因alias免票。|
|_project296–382，317/322/334/338/344/375|节点先扣1；tuple/list exact、≤300000、先n访问和n+1对象；dict≤100000，先2n遍历再测exact keys，之后n² traversal、(n+1)key_width scan、key_width hash及2n+1对象在输出dict/插入/排序前。六种typed record逐类收费、2f字段访问和2f+3对象先于构建；RuleSpec tuple元素all前先扣n。byteshex前4B+32 scan/8B scalar/5objects，≤1MiB。没有foreign len/iter/hash前门穿透。|
|_encode385–424，401|safe投影先按上行计费；普通JSON委托前2M traversal/8M scan、6M scalar、M+64对象。合法每个逃逸chunk≤M UTF8且≤4M字符存储；6M是yield前chunk/encoder固定块，不把yield后的8len误作其前票。yield后UTF8再先扣8len+1 scan、8len scalar；append前再留data长，末次bytes前留output长并扣copy；finally先清safe/output/encoder/chunk/data，释放本次增量，只留结果bytes。投影标量已支付但内部树退出后不能继续冒作外部raw的票。|
|_hash427|exact bytes，真实len先扣hash、128scalar/1object后digest；返回hex保持保守票。|
|_records435，439/441|exact tuple≤100000，4n+1 traversal在row/三个exact TermInput检查前，不执行数值解析。|
|_identity445，448；prepare713|exact tuple2，各str非空≤16384，_text收费；2项sum/身份比较固定检查在已有该字符串扫描块内，比较另扣总长scan。|
|_definitions454，459/467/477|rule≤100，disabled≤rules；每ID先_text；重复/disabled比较先按候选数及ID长扫描。disabled[:pos]同时持有≤100引用由4rules+disabled+4对象块覆盖；ids builder前票仍须修。raw与flat D各_encode；逐body先len(disabled)+10遍历、24对象再构建，字段不从恢复结果猜。|
|_read_syntax_json510，518/587|exact bytes≤M；UTF8/JSON普通委托前8B+1 scan、4B+1 traversal、12Bscalar/8B+64objects，字节预扫深度≤32。number callback固定拒绝，pairs≤固定白名单长度，48n+1 traversal/1024n+1 scan/2n+1objects在输出dict/重复key/hash之前；被库先生成的pairs与UTF8树有前述整块，不依赖hook后补。|
|_syntax_native599，607/611/614/617|每node1，list n遍历/2n+2对象后tuple生成器；fixed record字段检查与重建由2f遍历/2f+2对象块覆盖，类名最长固定，无任意导入。|
|decode_rule_definitions621，632/639/642/645/649|每body先32 traversal/2f+4objects，再RuleSpec；enabled/disabled逐比较先len(disabled)+1遍历，canonical比对前len和scan。JSON树票保守不释放，覆盖返回原生rules及receipt，不将投影结束理解为raw已消失。|
|_prepare_profile_material674，729|stage1 text二次UTF8前8len scan/4len scalar；structured借_records/_encode。stage2 source tuple前4n遍历/3n+1对象；SourceRecord前留1并_hash；stage3定义。外部raw/编码长期保留另4*(input+source+defs)scalar、2倍对象+8；发布前stage8 receipt及对象票。finish=False内部record也由+8固定控制余量覆盖。|
|_consumer_definition797，802/816/818|exact dict固定1–3keys；8n+1遍历；refs≤100000，先8r访问后fixed2key/ref检查，编码再走_project/_text。定义实际保留query或constraint原字段，无伪造enabled/references。|
|_selected_layer826/_selected_source850，854/870|各层exact tuple或ProfileInputLayer，UTF8解码前8B+1scan/4Bscalar；即时临时str丢弃后release。source四字符串走_text，content摘要先_hash，source.text≤65536解码先留4B、比较先8B+1；structured occurrence tuple先4n/3n+1。释放过晚是保守高估，不可因此允许提前复用。|
|_layer_from_json873，875；selected895，951/958|固定3key/hex exact，fromhex前4len+1 scan/lenscalar；identity只转固定2tuple。encoded input/source/D各_read_syntax_json前块后原样重编码、3对bytes比较按实际两长先扣。最终raw/encoded retention4Σbytes、2Σbytes+8及receipt保持caller责任。|
|decode_selected_material1007，1011|固定3bytes入口、每≤M，无额外数据遍历；新ledger始于被调用私有实现。|
|production154/186|exact ProfileMaterial/四exactbytes≤M、rules≤100；重准备从raw形成checked，无第二matcher；四对前像_same_bytes按实际两长先扣。source重编码及比对后真实del/release。|
|capture65–96、semantic hooks|definitions/context/catalog只捕获同次真实返回引用，分别4n+1/2n+2、n+1、固定4/1收费；allocation40 traversal/24objects/1024scalar先于slot，真实原L对象，不复制分池或从payload推L。slots bootstrap后置见BR-F02。|
|before_projection/rows98–114、execution717–757|6普通原投影的16M traversal/32Mscan/24Mscalar/8Mobjects在delegate前；7再16M/24M/8M/2M覆盖UTF8、rows切片/encoder并持。所有块保守留至返回，不将stage6释放供stage7再用；hash问题BR-F01。projection原node/output/depth门保留，未把普通delegate称opaque。|
|production208/211/213/221–242|实际slots/rules数前8s+4r+8访问/6s+6r+16对象，再分配OriginalAllocation和子record；stage8 Catalog前8M遍历/16Mscan/8Mscalar/2Mobjects、实际_hash前扣；receipt前64遍历/64objects/1024scalar。唯一成功record保留material/native/原defsCatalog/原L/五编码/wire；没有ledger live0或return=释放的说法。|
|ReadonlyObject.__getitem__176|返回后线性读view，本次R不调用它。未来consumer对这些访问仍须其T/S/H合同，不把readonly视图当无限免费API。|

C五域的限制实际执行均为消费前拒绝；BR-F01/F02显示“通过现有exact/差1测试”仍不足证明真实工作在前票内。未发现其余大数据循环存在无长度/无费用的具体反例；这不声称全部合法输入必成功（紧C预算可先合法拒绝），也不量化CPU/RSS。

## 完整恢复的实际费用与生命周期

restore.py:1101–1204先按原decoder读/校验/恢复：safe_source、safe_defs、safe_records各消费后del并分别释放4J scalar/2Jobjects；safe_reason/safe_payload/encoded_payload在1202真实del后，1203–1204释放同量。不是只移动ledger数字留下safe树。

1207–1212先原A16 prepay（32J traversal、128J schema、4(J+S)copy），再128N+128 traversal、1024N+1024 copy/scalar、256N+256objects固定receipt/slot块。之后才fullview freeze，再原每child一次16c；同一次R内不能重新begin或重复stage。原16c三池/原L及费用公式完全未改，C/restore的费用没有混入原W/I/O。fullview不会再次parse/compile/evaluate/issue PV。

1034–1098实际freeze收费：每节点先1 traversal；dict另size traversal，在builder前16size+32copy；sequence builder前12size+32copy。精确canonical类只做固定_EQUAL_FIELDS查找（预付其整个长度），返回已有immutable叶，不asdict/deepcopy/重发PV。raw/native两个来源在冻结期间同时可达。new `_freeze_projection`先留2Jobjects、4Jscalar、64copy，再构造7字段外层和深freeze。A16块覆盖固定frame、临时7字段映射、wrapper/receipt快照；新增预留不可转给opaque，也不占原16c池。

实际对象上界可以由这套固定schema映射，而不能仅引用注释：m字段dict builder/finaltuple/pairs/wrapper按≤5m+4对象或引用；n元素sequence同时builder、tuple、wrapper按≤2n+5。dict键均来自已验证固定schema（最短work/rule/term/span等4字符），其JSON键与标点给≥7m字节；足以支付dict本身及父边。非空string数组的最短叶是`""`，数组字节≥3n+1，n≥1时2倍字节≥2n+5；triple固定3，其他数组元素为非空fixed记录/元组。空数组局部5大于2*2=4的1票差，均挂在已有固定key/record字段上，由其键的严格余量覆盖；native不存在可任意嵌套空数组链。canonical叶占JSON recordType/字段等至少固定标签空间，freeze本身不增加其内部对象。原safe树此刻确已退出，不能把2J同时支付旧safe和新view。实际7/15/11及其固定嵌套native结构均被覆盖；2J是逻辑对象/引用界，不含Python allocator字节。

遍历也有来源：普通叶1≤其JSON表示长；dict额外m访问由固定键字符支付；sequence每元素一次node递归由对应原位置/标点支付；canonical叶的固定类表查找由其recordType表示的固定空间支付。因此freeze新递归及固定查找不超过该payload的J字节界（J还含rows和preimage），不是把“单次walk”直接当全部实际访问。copy每容器16m+32或12n+32按字节/标点可保守归入原A16 4(J+S)与全局copy池余量；实际所有copy仍独立charge，低限会在分配前拒绝。新增4J scalar为既有不可变叶/issuer保守转交票，不产生新的hex/UTF8副本。

全局池未变：新objects是在safe释放2J后换成新view2J，旧8J+16M+2048N+4096 cap无需扩大；新增scalar4J换回刚释放的safe4J；新traversal≤J，相对于旧512J+64M+65536N的保守阶段余量是新增实际费用，不能声称整体R≤W/I。没有以池大为由忽略前票。旧readonly restore_budget 的scanner/trie/49字段key/integer limb算法本次未变；身份已核，未冒称这一轮重新穷尽旧算法全部反例。

1337–1361返回前，唯一_public operation内保留projection/children/inner_batches/retention；retention取**全部**仍保留的ledger.live快照，而非只2Jview。包含caller context、native/issuer票和可能即将消失的解析临时物，是保守界；随后usage/peaks快照，之后不再收费。成功所有child完成后才RestoredProfileResult发布。finally清所有独立native/view局部并decoder.drop，cleanup/finish仅终结本R；成功引用由outcome交caller，不能据live0声称已释放。失败清outcome，原异常不作为context交付；usage/peaks/live/三constructor/freeze中途/最后child的新增普通故障专项均真实通过。terminal BaseException分支也清outcome/decoder再抛；本轮没有模拟OS终止，不能把受控MemoryError当真实OOM。

实际smoke J98723，view外7/内15，retention.objects202953、scalar1496642；terminal success且ledger.live六域0，返回真实view仍存在。43项专项还验9类fresh-process fullview、字段signature/原rows、readonly/PV发行、所有累计/并持域exact与差1、最后slot失败及公开frame/issuer清理。它们支持实现路径，但不是全输入内存或性能证明。

## 处置与交付边界

- BR-F01开放：须前移hash，不扩cap，真实低限委托次序复核。
- BR-F02开放：须前置控制票并处理三个builder，不扩cap，objects0/63/64及失败不可复用复核。
- 完整view新增freeze/保持/成功唯一转交/普通异常清理：本轮范围内通过；未找到要求扩大原R cap的具体反例。修改上述问题若触及此路径，按真实delta决定复核。
- 未宣称正式producer来源/Job受理/selected K0..32/原snapshot/worker/Store/H租期已接线。返回retention是费用描述，不签权限；这些仍为未来真实owner门。

本报告限定普通Python Exception/受控故障及固定源码静态算法。不是RSS/CPU/产品容量线证明，不承接他方238或1024测试为本轮运行，不替代全仓check、完整数学/89/40或指定双模型/CI/双OS/真人验收。
