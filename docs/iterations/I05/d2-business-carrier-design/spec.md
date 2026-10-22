# D2 业务/stage carrier 与来源身份设计提案

本候选提出可审查的 G02/G03 新规范，尚未获 D0/T03/T05 采用，没有产品 writer、源/锁修改或运行许可。基线为 `dc3fc7768167f206e09b410da4f737199d2c5e18`，同树同分支，仅新增两个 `d2-business-carrier-design` docs 前缀。旧 D2 的57件逐件 current=固定Git=SHA，旧三过程JSON格式exit1和P3原件保留；本候选技术属性统一写 `function.__code__`。

## 1. 版本边界与显式协议

旧 D0 的 `runtime-header/1` 全部18键与原文件冻结；旧 `consumer2.1/profile3` 和其 header→observations→terminal 流语法均冻结。已收D1纯提案（ref `86d6297a8cac5ad780f1be4416ec9052b82f3aaf`）指定 protocol/consumer3.0.0、profile4、header2及三种receipt/provenance新版本。业务新流只面向这一尚待完整物化/独审采用的新组合；header2仍同18键，仅按D1精确literal index升级format/profileId，不塞业务字段。source22声明/23实际、frozen actualSource=null与外置self-pin保持。**新流不是旧流语法的无缝扩展。** 本提案的新名称为 `i05-business-stream/2`、`i05-business-context/1`、`i05-business-stage/1`、`i05-business-observation/1`、`i05-business-terminal/1`、外部 `i05-business-carrier/1`。header键数相同不能证明新流被批准，也不能把旧header/1原raw改写为header/2。

后继外部批准的consumer-contract3.0.0、profile4/descriptor、header/2及独立business adoption record的新流文法精确pin必须在launch前一致；完整v3规范目前尚未接收，pin=null。caller显式选择批准的 `expectedStreamVersion`，不得窥第二行自动升级、按key猜版本或从包内自报批准。三exact argv仍保持原值；新模式不增加环境隐选、stdin参数或任意path。runId由新probe本次实际生成，caller的attemptId是外部调度标识，两者只是关联，不授issuer/权限。

新流的具体文法如下，每行严格UTF8 JSON、无BOM/duplicate/nonfinite/尾数据，LF终止：

`header2 LF context1 LF (stage1 LF | observation1 LF)* terminal1 LF EOF`

header2必须按当次批准的完整v3 header/2 schema严格解析；这份实际原行bytes不由新codec重编码替换。旧header/1只由旧decoder解释，新decoder不得将其提升为header/2。context恰一条且先于任何stage/observation；后续帧 `streamVersion` 均为精确新版本，frameOrdinal自1连续，runId相同。每个observation的stage严格串行，最终一条observation帧；终态最后唯一。stage记录实际开始/返回/安全拒绝/unknown，不冒尚未发生事件。未开始/未到达项仅由caller对批准stage plan派生，标derived-plan，不能冒child观察。详细字段类型与required/联合分支在 `wire-grammar.json`；它是本提案完整有限文法，不是已经生效的公共schema。

旧decoder在prelaunch看到新profile/stream pin即拒绝、不launch；若误收新raw，旧header可解析，但第二行business-context不是旧observation，必须停止升级完整结论，保全全raw并按旧incomplete记录，不能跳过未知帧继续计417。新decoder面对旧profile/缺context、未知stream版本/帧kind/ordinal缺口/附尾数据也拒绝，保实际raw；不静默回退旧语法。新profile批准前所有拟运行都not-started。forward-delta列出必须独立接收的版本增量，未改旧文件。

## 2. 业务上下文与完整stage返回

context明列runId、旧完整观察格式身份、实际mode/selector、完整/所选有序inventory及摘要、320/417/83/106/54/50原上下文账、writer/asset/lock/resource声明与实际证据、Python/工具/八distribution、语义/policy/budget版本、instrumentation、完整nonClaims。每项是有状态的EvidenceValue，必须区分 declared、observed、unavailable、not-applicable；observed必须有实际原件/帧来源，不能把批准预期抄进actual。源码自己的批准pin只在caller外部negotiation中，context不内嵌自身source SHA。source/frozen差异继承D0，context补业务材料，不改header含义。

固定资产的inputProjection、sourceRefs、contextStatus、全部显式参数/API/调用plan进入逐项descriptor；不把expected/golden/allocation/expectation置入输入。新帧不会使417成为已运行；full恰固定资产原序417，B1两档各一measurement，另保完整full inventory，不拼合B1冒full。旧83/106/54/50和320dataset背景独立保留，不以actual观测数覆盖原上下文总量。

每个stage有stageId/ordinal、前序、批准API与完整显式参数、真实event/开始结束证据及hook计数、完整返回pieces或安全失败引用。piece按原返回字段/slot的完整有序目录逐项列出：result、payload_json、rows_json、typed view、wire、sidecar、source_encoded、definitions_encoded、catalog_json、原metadata、公开ErrorFrame或私有安全diagnostic。返回字段目录由该API精确owner layout pin约束，数组/tuple/map次序、重复、null和末项全部保留；不允许只留摘要或只取schema认识的字段。新出现字段不裁掉：原bytes/安全可导出值全留，并以layout-unrecognized阻断完整适配，不能已知完整成功。

每个piece在stdout stage帧内携带完整base64字节、真实bytes/SHA、representation、codecId与original-field pointer。representation区分captured-original-bytes和owner-encoded-return-tree；后者是本次明确编码的返回对象，不能冒原先已有wire bytes。caller从实际raw帧取出完整bytes，存为明确登记的artifact，再以固定root/path/bytes/SHA引用进入外部carrier。**这是一份明确版本化、有清单和映射的外部文件，不是默认存在的隐式sidecar。** probe不按其中locator扩读包外。

`i05-return-tree/1`为新有限无损值文法：exact null/bool、十进制整数原值字符串、Unicode string原码点、bytes原base64、list、tuple、保持插入顺序的string-key map、明确批准record字段序列。所有节点exact tag/keys，map/record键唯一，list/tuple序列可重复。仅允许精确builtins或由owner明确接收的exact canonical class adapter；禁止任意getattr/迭代协议/repr/str/exception args。浮点/Decimal/Calendar/Number/graph等不得按猜测转换；需对应owner codec/layout pin和完整字段文法，未给则unavailable且完整语义接收阻断。未知对象不能通过本通用树声称无损兼容。

拒绝终态partialView=null只约束当前未返回的视图，不能删除此前已returned的完整pieces。callee真实return发生但完整piece尚未发完即预算/硬停，stage语义标return-seen-output-incomplete，保当前全部raw/先前完整stage，不能标returned-complete。cap未预留足够输出时先拒开始该stage；无法预知或opaque返回后超限仍incomplete，不隐藏已发生调用。不得重跑以补造首次缺失raw。

## 3. 原metadata、codec及同次来源

旧reasoningSource的完整字段/原codec不在批准27件纯规范中，不能猜字段或给任意JSON签“兼容”。metadata binding必须逐项保：原bytesArtifact、originalCodecId、原codec源码pin与布局规范pin、完整原preimage/digest recipe pin、解析后的return-tree（若有）、新转换版本/pin、compatibility状态/缺件、same-issue关联与原handle证据。没有旧codec/layout pin时允许保存获准取得的原bytes作为opaque-preserved，但 semanticCompatible=false、parsedTree=null、compatibility=pending；不得因此消费旧helper或把错误bytes改写为新display source。

新display `i05-scope-content-source/1`继续只作内容摘要；旧helper接收的必须是本次prepare原样返回的真实reasoningSource对象和reasoning_result。新carrier/JSON不能还原live对象、重新发行material、allocation、capture、issuer或授权。若原值并无既有编码bytes，必须先由owner接收确切export codec及完整字段manifest，再将本次export标owner-encoded；不得凭借本方案声称已经有“旧原wire”。旧raw或metadata中的原digest逐字保留。

same-issue分三层：① producer/source/class/codec的已批准不可变pin；②本次同进程真实source handle、material/reasoning result/metadata/graph关联；③只作取证引用的sessionId/issueId/referenceKey及artifactIds。③的字符串相等不能证明②。handle不跨进程传对象或凭地址/id()认证；live verifier由owner指定精确源码/函数及预期对象规则，真实执行在另授窗口。它在prepare→project同次链上核对象未换/原输入一致，并生成受限实际witness，指向当时metadata/graph/producer原件；caller校核该witness与真实code/来源后才可记observed-match。缺verifier pin/真实handle/完整witness均pending，观察不等则mismatch；不能填预计true。

本提案给了完整容器、状态及guard，不宣称旧codec和live映射已知。`missing-materials.json`逐项给所需材料的精确类型/owner/拟接收字段和未获批原因，不读取产品函数体、费用WIP或actual来填空。仅此缺材料阻断实际G03语义兼容及运行；容器设计本身可以独立审查。

## 4. artifact身份域与BNode/digest

每个新不可变graph/parse/producer artifact有run内唯一artifactId、完整原bytes/codec/layout/pin及创建stage引用。query/SHACL/RDF evidence的每个明确term槽必须指向其实际输入graph artifact所属domainId；同一图的全部声明槽共享一个BNode双射，未声明raw/source/词法/ID/digest保持exact。独立parse即使label相同也不同域；只有owner核验的显式转换关联可联系两个artifact，不能以内容相等、同label或caller自行复用domainId合域。复制/推导产生新artifact，记录父关系和真实映射来源，不隐式继承node身份。

完整比较仍必须先双方schema→各端全部graph wire canonical→按明确domain一次全域双射→完整其余值比较，唯一入口保持matches语义；本窗未调用模型。最多8BNode仍只是数学小例界，不成为产品容量。37项expected/typedMath/参数/来源不变，十四held bytes不重签。不同domain之间不做全局改名，缺graph→consumer归属witness时identity-binding=pending，不能oracle-match。

原raw digest、原metadata摘要、原source/definition/payload/rows摘要与新编码摘要全分域。label会影响原wire或内容摘要时不删、不统一重算、不改原件。比较器可另产生显式mapping witness：绑定双方各自全部原artifact摘要、domain配对、完整双射、比较规范和code pin、逐槽关系结果；其relationDigest只描述这一关系，不替代任一原digest或同次发行凭据。旧digest的recipe/preimage未知时原字符串可保，但verification=pending，不能声称已验证。

## 5. 摘要preimage与无循环

`RawSHA(b)=SHA256(b)`只对原字节，base64严格canonical decode后按原bytes计长。`FrameSHA`对一行JSON的原bytes，排其终止LF；caller给byteOffset/byteLength，原stdout对应range全同。UTF8严格、禁止CRLF替代LF；若实际坏CRLF/半行/BOM保完整raw并incomplete，不修复后比较。

新结构摘要采用 `H(tag,value)=SHA256(UTF8("ontolearn/i05/"+tag+"\u0000") || UTF8(C(value)))`。`C`定义为严格JSON的对象key按Unicode码点排序、array原序含重复、整数十进制无+或前导0、bool/null小写；字符串以双引号、quote/backslash和U+0000..001F按JSON短转义或小写四位hex（明确优先\b/\f/\n/\r/\t），其余有效Unicode直出，无slash转义/normalization/BOM/空白。新摘要结构不接受浮点；原浮点wire保原bytes或获准codec，不能C重编码吞差。精确参考是指定Python `json.dumps(...,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)`在上述无float域的UTF8；合成vectors提供实际preimage base64与hash。不能用格式化文档的bytes代C。

域tag逐项固定：inventory-full/1、inventory-selected/1、stage-plan/1、return-tree/1、metadata-export/1、artifact-domain/1、mapping-witness/1。每个摘要对象仅取grammar中明确的preimageFields，不把自身digest/后继receipt/process/manifest纳入。raw-byte SHA与H结构摘要不得互填。

terminal仅可携带priorPrefixBytes/priorPrefixSha256，后者是stdout从offset0至terminal行起始之前的原bytes；不含terminal本行，不签完整流。完整stdout/stderr SHA由caller在真实结束/join后算。顺序为批准源/协议/immutable build票→真实raw及runtime witness→提取pieces及frame index→carrier→独立comparison/mapping witness→外部完整evidence manifest→后出validation。carrier不引用comparison、包含自身的manifest或后出的validation；manifest排自身和validation。保持T03拟runtime-validation-receipt/3的1241字段结构：另提明确 `i05-business-validation-binding/1`（先于manifest/validation），它指同attempt/carrier/原raw/immutable build-receipt/3及各run core，**不指后出的validation**；新runtime receipt/3的runtimeEvidenceManifest.files列binding、carrier及全部原件，由新consumer3的规范关系逐项核同。无需偷加runtime receipt顶层key；完整v3实际pin及这项业务增量仍待T03/root接收。不回填build receipt/2或/3、provenance、旧header/raw。格式化这些JSON不影响原raw字节身份，新文件自身的RawSHA总在其后继外部记录。

## 6. 严格失败与采集边界

四状态仍为not-started/pre-header-rejected/incomplete/collected，header/terminal各absent/malformed/parsed。not-started没有child/runId/raw/帧/artifact，caller failure指先于launch的批准/协商首错；拟argv不是实际运行。真实dispatch后stdout/stderr即使0字节也必须列，信号非null时exit=null，未知终态保null。malformed帧索引保原坏range/原bytes，parsedValue=null，不能填合法预期。observedPaths及piece/slot索引保实际false/null和全部原件；“null存在”与“未观察”由状态区别。

新stream和carrier的协议诊断是私有collectionFailure reason枚举，不新增公共errors；public ErrorFrame仍原四字段，私有canonical diagnostic仍独立origin/reason/classification/stage/slot/domain/ruleId/location与harnessStage。不可把路径/堆栈/异常文本塞其中。unknown只安全INTERNAL_ERROR及有限stage，complete=false；已返回安全字段/原stderr仍按受控证据域保全，不由新codec打印任意对象。

collected要求同一selector全有序ID、所有实际stage完整已返回pieces与批准layout、全部必要身份/metadata/graph绑定可验证、完整header/context/terminal、真实exit0/signalnull及无collectionFailure；known业务拒绝可完整采集但不变业务通过。原metadata兼容pending、缺同次witness或必要piece都不能标collected。carrier文件/manifest完整仅指实际存在原件都列，不推出运行或业务完整。firstCollectionFailure独立保run级实际最早采集/协议/绑定失败；每个observation的canonical首错仍在原stage/error piece保留，已知业务拒绝可完整采集并继续下一case；同一observation链之后的not-reached必须指该链实际阻断，不用任意RESOURCE顶替F1/D1/R1/O1目标。stage先成功、后拒绝的原顺序不可改。ProcessLifecycle另保完整命令上下文、实际dispatch/目标handle、cancel request/stopping/真实终止/readerjoin/引用释放/计时/物理票状态；probe terminal不能自证这些caller事实。

旧descriptor1MiB/input8MiB/合9MiB/512上限实际417、单输出32MiB/总stdout64MiB/terminal64KiB/120s边界在新提案仍为不得悄改的前置；新帧/编码开销计入同总量，不丢字段迎合。外部carrier提取可不复制bytes，仅明示原raw range与已列artifact；若完整新文法实际超旧cap，必须提出独立版本/预算delta，未批准前incomplete/不得开始。逻辑cap不签native/caller/ABI/loader/drain/取消物理票；request/stopping/实际终止/readerjoin/引用释放分开。

## 7. forward增量、采用与未决

forward-delta分别给D0、T03、T05提案与双向拒绝。旧完整锁23、待收D1完整锁26、canonical runtime23、source声明22、八runtime distributions是不同集合。已按root追加授权读取D1五件精确纯设计原件，26包/六直接项逐项来自dependency-plan，未读真实锁/产品。新完整v3 descriptor/依赖manifest及实际组合pin尚未生成并接收，前置不能launch新组合。若新codec/serializer引入额外canonical模块或更改四函数/Python域，另显式闭包delta，不能自动把23变26。

本窗可完成“明确文法/字段去向/摘要/失败/身份guard”的设计接收；实际旧codec/owner-return-layout/live handle verifier、T03完整v3新规范的独审采用及所有真实来源/权限/运行保持pending。D1的26包纯方案已经限定收件，不再作为未收到的输入；9冲突/21old-only逐owner真实兼容pin仍null。后继具体产品路径及唯一writer仅在方案接收后由root确定。无需读未批材料来完成这一容器方案；缺口逐项不能通过的guard已明确。

旧G01/G04/G05、真实F1/D1/R1/O1 API首错、独立费用/allocation/issuer/capture、Job/Store/whole-H、完整417/wholeOracleComplete=false、父137/S1/B1、平台/真人/指定双审/CI/develop仍不关闭。本候选只在本方新prefix显式stage、cached检查后本地提交；root另派新独审，作者不自认Pass，不push。
