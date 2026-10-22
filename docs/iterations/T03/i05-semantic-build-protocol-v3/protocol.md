# T03 I05 semantic build protocol v3.0.0

2026-10-22。本目录是前向完整新规范候选，待原T03全文接收、固定candidate及fresh独审、总控精确设计接收；不是旧D0的覆盖或产品实施。D1纯方案已由总控限定接收（旧过程86d6297a8cac5ad780f1be4416ec9052b82f3aaf）；旧D0 c3eb0694daad26527cc3a1eb0127ed5033f2be25 的66件与23包规范完整冻结。新版本完整保CR来源、路径、真实CodeType、失败/信任/收据/观察合同。所有future actual pins保持null/空，executionAuthorization=false；没有安装、resolver、build或runtime实例。

## 1. 固定输入、版本和采用方式

正式批准base=5f910b52c69d86a1076b2032e5d3c63e715947f3；本纯文档作者树冻结输入HEAD=86d6297a8cac5ad780f1be4416ec9052b82f3aaf（不是新组合产品base）。旧offer/adoption/D0/D1完整历史保留，输入与本目录原bytes分别由包外input-manifest/candidate-manifest列身份；不预填未来自身commit/hash。JSON Schema2020-12 shape与本文、consumer全部跨字段规则同时必需，版本本身不授权产品读取。

| 文件                                                     | 完整版本 / ID                                                                       | 用途                                                  |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------- |
| build-provenance.schema.json                             | i05-source-package-parity-build/3 / urn:ontolearn:i05:source-package-parity-build:3 | E0后置包内完整构建声明                                |
| build-receipt.schema.json                                | i05-build-receipt/3 / urn:ontolearn:i05:build-receipt:3                             | E0包外immutable build receipt                         |
| runtime-validation-receipt.schema.json                   | i05-runtime-validation-receipt/3 / urn:ontolearn:i05:runtime-validation-receipt:3   | 后出完整runtime receipt                               |
| runtime-header.schema.json                               | i05-semantic-runtime-header/2 / urn:ontolearn:i05:runtime-header:2                  | source/frozen完整header与失败观察                     |
| profile-descriptor.json                                  | i05-semantic-build-protocol-profile/4，id=i05-source-package-parity-v3              | 完整未批准profile                                     |
| consumer-contract.md                                     | 3.0.0                                                                               | 完整source/frozen/caller strict合同                   |
| field-responsibility.json                                | i05-d0-field-responsibility/4                                                       | 全部1241显式property pointer与actor/18安全码          |
| dependency-specification.json                            | i05-protocol3-exact-dependency-specification/1                                      | 全26包版本、各原block及全部artifact来源与六直接项规范 |
| guard-adoption-matrix.json / guard-migration-contract.md | 三scope完整逐项账/行为合同                                                          | 历史45、semantic33、parent58互不混用                  |

D2只可在新规范精确接收后按四schema同版映射、另授权窗实施新consumer并供新第23 pin；旧2cf仅祖先。T03四writer/锁与原I05/T01共享源各有唯一owner，产品/锁/collector/consumer没有在本窗口修改。G02/G03 business carrier由I05单独作者维护，本文不新增其schema；精确接口依赖另见interface-adoption-contract.md。旧T05实现限定收件及allocation/oracle后续独审原门不变。

## 2. CR-S：strict shape、集合与引用闭包

所有 schema 对象 additionalProperties=false；required 中每项必须存在。null 仅在 schema 显式允许处合法，不能用字段缺失替代 null，也不能用 null/unknown/空字符串冒必需实际证据。UTF-8 原字节、无 BOM、无 duplicate key（所有嵌套对象）、无 NaN/Infinity、无尾数据；布尔不是整数。source/payload/receipt hash 是64小写hex，ref/blob是40小写hex；SHA 算原字节而非重序列化，base64 算原字节。外部读者必须按有限精确 schema 而非 permissive object 接收。

`inputs.modules` 与 `moduleBindings` 恰23唯一 canonical 名/路径，顺序为 profile.canonicalModules；前22为6891供应，最后为经 D2 新批的 consumer，原2cf只祖先。`bindingId` 恰 `canonical:` 加 canonicalName。sourceCompilation.source 与相应 inputs.modules 的 ref/path/bytes/SHA/gitBlob 全同，Git source 不能转 installed 域；role 前22=canonical-module、最后=canonical-probe。bootstrap 是独立 `bootstrap-main`，不计入23。distributionCodeBinding 恰 `distribution:pyshacl.validator` / canonicalName=pyshacl.validator / role=distribution-module，不计入23。

四 function 名集合恰 semantic.reason、semantic.query、semantic.validate_shacl_text、Validator.run。前三 moduleName=ontolearn_engine.semantic、moduleBindingId=canonical:ontolearn_engine.semantic；第四 moduleName=pyshacl.validator、moduleBindingId=distribution:pyshacl.validator。不接受重复/缺项、同数异名或 dangling binding。每个 function.sourceCompilation 是其 module binding 同一 source/完整模块 compile 见证，不能换另一份源。所有 codeConstIndexPath 是实际记录的非空 co_consts 索引；同一数组分别在 source-compiled module 和 actual archive-extracted module 上逐步取 exact CodeType，再分别求 expectedFunctionCode/actualArchiveFunctionCode。每一步不是 exact CodeType、索引越界、反射 name 猜取、复用 sourceSHA 作 code 均拒绝。

inputs.resources 恰 profile 四 source，assets 恰两 source，pyproject/lock 与批准 dependencyRef 同源，writers 恰四路径 pyproject/uv.lock/build-engine.mjs/entrypoint.py（pyproject与lock两账全字段相同）。23+4+2+4 共33不同路径；profile/工具元数据另外列、不混计33。33项 before/after clean/bytes/blob/ref 须真实核同；AGENTS保护M不属于构建输入变更。profile 名/target/onedir/_internal/optimize=0/flag 固定，parent/default遵守本目录完整三scope迁移合同：历史a4d根保原43+两writer45，新semantic只33，新parent58逐owner供兼容实际pin后才具构建资格；不能把9冲突的两版字节同时要求在同一checkout，也不删除21old-only或永久拒旧flag。新 profile 只按完整有限表解除 rule_revalidation exclude，其余 exclude 与 collectAll/hiddenImports/copyMetadata 逐项按完整 descriptor 精确集合；不得 collect-all engine/quality 或 glob contracts/v2。

八 distribution 名集合固定 rdflib7.6.0、pyshacl0.30.1、pyparsing3.3.3、owlrl7.6.2、prettytable3.18.0、wcwidth0.9.2、html5rdf1.2.1、packaging26.3。每项 name/version/selectedArtifact 与实际批准锁同一条目，不能只比八个数量。完整26包锁（workspace/dev/build-tool/marker/extra/全平台wheel与sdist）严格按本目录dependency-specification.json全部26名版本和六直接依赖，由外部source/witness绑定；每个 distribution.allPlatformArtifacts 列该包完整 lock artifacts，selectedArtifact 必须恰为其中一件并符合真实平台/marker。requiresDist/activatedExtras/markerEnvironment 保实际完整值，不因未激活marker删原项，rdflib[html]→html5rdf不得漏。buildToolDistributions 保完整同形来源/RECORD/许可和实际工具身份；build工具不强制混入八runtime集合。现有版本是设计目标，不是实际安装事实。

## 3. CR-A1：固定根域与真实普通文件

schema 的 root 是字段定义中的 const，实例不能任选根。所有最终普通文件（receipt.directoryFiles/executable/embeddedProvenance、runtimeComponents.bundleFiles/licenses、distribution license.bundleFile、bundleMappings.path 的实体、dynamicChecker.bundleFile、archive.location.file）固定 bundle-root。payloadFiles 固定 meipass-root，恰 `_internal` 下所有普通文件、排唯一 provenance；不是 bundle 根列表。Git source 根、approved-installation、approved-artifacts、approved-witness、approved-logs 分域；evidenceRoots 中是封闭 ID，root 的外部 approvalRecord 才把这些 ID 绑定到获准真实环境与前缀，不在包内放任意绝对 locator。

同一 data 文件两账必须 `bundlePath = "_internal/" + payloadPath` 且 bytes/SHA 全同；也须存在 receipt.directoryFiles 同一项。checker 根路径固定 `_internal/contracts/python/contract_v2.py`，payload 对应 `contracts/python/contract_v2.py`。唯一后置 provenance 根路径 `_internal/provenance/i05/source-package-parity-build.json`，payload 排除 `provenance/i05/source-package-parity-build.json`。四资源、两资产、lock 的 meipass 路径是 descriptor 唯一固定白名单，无 fallback。

executable.path 是根 `ontolearn-semantic-parity` 或 Windows 的 `ontolearn-semantic-parity.exe`（由批准目标OS唯一决定，不是两个副本）；root directoryFiles 中恰同一真实启动文件。runtimeComponents 必须分别保 python、stdlib、pyinstaller-bootloader 和实际 dynamic-library/platform-runtime；不能以 enum count 冒闭包。bootloader.bundleFiles 必含同一个 receipt.executable，path/bytes/SHA全同；不造 `_internal` 同名文件，不把 PE/Mach-O 片段伪成普通文件。确需片段见证须另批准布局 delta。

path 语法只第一层：拒绝空、绝对、反斜杠、drive/UNC、NUL、URL/冒号、`!`表达式、空/`.`/`..` segment、尾slash/点/空格。外部核验还拒绝 casefold/Unicode normalization/平台保留名/短名等别名、重复规范名、symlink（包括链中任一段）、hardlink 身份别名与根外 escape。root/caller 在获准根中实际 containment 与 lstat/真实普通文件核验；不能照字符串拼命令。包外 evidence 不进入最终 bundle 根；不为 nested PYZ 造普通文件。数据 raw RECORD 的原 pathField 不受安全 locator pattern 改写，因为它只是证据。

## 4. CR-A2：封闭 archive 账、第四函数与 raw witness

archiveId 唯一并仅可 carchive-main、pyz-main、external-pyc-main。location 是严格 oneOf：只有 file 或只有 parentMember；不准两者、空对象、任意字符串链/URL/cwd。carchive-main 必为 kind=CArchive、location.file=同一 root executable，archive bytes/SHA与该实体全同；depth=1。pyz-main 必为 kind=PYZ、parentMember.parentArchiveId=carchive-main、exact memberName/raw bytes/SHA与父完整 inventory 同一行全同；depth=2，无 file。external-pyc-main 只有经 root 批准 descriptor exact toolchain/布局时可用 kind=external-pyc/location.file 的实际普通文件，depth=1；它不能替代必需 canonical PYZ项。本未批准 descriptor 没有授权任何实际 external-pyc。

父必须先出现、唯一、无环、depth≤2；本版本禁止 PYZ 内再嵌 archive。complete TOC 保实际顺序、所有 name/kind/raw bytes/SHA，不只收23相关项；每容器 inventory 名唯一。actualArchiveCode.archiveId 必引用现存账项，memberName/memberKind/rawMemberBytes/SHA须与该容器 inventory 精确相符。每项 rawWitness 是 approved-witness 下真实解码/提取原字节保存件，同 raw hash/bytes；它与 final bundle 普通文件是两账，不能加入 directoryFiles 伪装。extractorSource/extractionMethodVersion 必绑定批准工具源码及真实运行身份。

23 canonical.actualArchiveCode 必是 pyz-main/PYZ-module 的真实 code；bootstrap.carchiveScript 是 carchive-main/CArchive-script，最早 main guard 在类发行前转 canonical main，canonical 对象唯一。第四函数单列 pyshacl.validator installed source→selected pyshacl artifact→RECORD row→实际 PYZ-module→same co_consts path function，不能用全TOC里一个名字代模块 code binding。module codeEqual / bootstrap codeEqual / function codeEqual 都须逐完整 fingerprint 真等，不接受人为 true。actual 工具若产生超此形态（如额外容器/层次/代码变换）先报确切版本/布局 delta，保首错与全TOC，由 新协议/D3修订后重审；既不总拒绝规避必需功能，也不自动开放递归 locator。

## 5. CR-C：checker 与 Python/code 域拆句（A2.5/N-01）

E0 对23 canonical、bootstrap、四函数，分别比较批准 source compile 与实际 archive 提取的 exact CodeType 指纹。

E0 对 checker，只比较批准 Git source 与实际 bundle data 原 bytes/SHA，并对二者分别 source compile 得 sourceCompilation.fingerprint 与 expectedBundleSourceCode。dynamicChecker.stage 固定 build-source-to-bundle-data-only；其 codeEqual 仅这两项完整指纹相等。checker 不要求进入 PYZ，构建声明不存在 runtimeLoaderCode。真正 resources.CONTRACT loader 的 get_code/对象/cache 是 E1 runtime receipt 的 dynamicChecker.runtimeLoaderCode，由 caller/header 回绑。

唯一 objectAuthority 是原 resources.CONTRACT；spec/name/origin/实际 loader 与消费者引用须核同。原 sys.modules 无此注册、registrationRequired=false，不能因此另exec、增加 alias、重注册或改公共 resources.CONTRACT。checker 顶层只读 schema/registry/errors，resources 另读 registry/lock；允许 semantic_identity、普通error目录及 validate("error", value)。不调用 resource_manifest/build_request/execute_request/derive_dependencies/permits_transition，不读 dependencies/states/fixtures 等额外 v2。

fingerprint 严格保原四字段 algorithm/sha256/pythonCacheTag/domain，domain 原字面仍保以兼容算法返回shape；真实域由 sourceCompilation/actualArchiveCode/expectedBundleSourceCode/runtimeLoaderCode 外层位置决定，不能凭 domain 字样冒 runtime 事实。algorithm=i05-code-object-marshal-filename-normalized/1，exact CodeType 递归 co_consts 中 code 只 replace co_filename=<i05-canonical-code>，保字节码、flags、name、qualname、lineno、linetable、exception table、所有常量及其他字段；marshal.dumps(...,4)→SHA256。不删除字段消差，不拿 sourceSHA/raw archive SHA 填 code fingerprint。

source compile=批准原bytes、实际source路径、exec、dont_inherit=True、optimize=0，使用实际构建解释器；compile不是执行 source。Python完整 implementation/version/hexversion/buildIdentity（versionString/buildNumber/date/compiler/apiVersion）/cacheTag/magic/marshal/optimize/byteorder/abiflags/platform/architecture/flags/compilerExecutable 全部保留。每 compile/archive/runtime 的 build/cacheTag/magic/flags/optimization和算法须同域；相同cacheTag不足。codeDomain.marshalReferenceStability=measured-same-domain 在E0只指 sourcecompile↔archive 的实际测量，不预签 E1 loader。E1独立 fresh/cold/warm/cache 重复 get_code 与真实 `function.__code__`，exact CodeType/相同canonical对象/稳定指纹逐项保见证；缺get_code、非exact类型、缓存/引用intern导致差异保首错，新算法版本/source/consumer/schema/工具共同delta后重审，不降sourceSHA。

## 6. CR-A3：RECORD、许可与 runtime 保全

distribution 与 buildToolDistributions 都保 selectedArtifact/allPlatformArtifacts、完整 METADATA/Requires-Dist/extras/marker environment、record原文件与recordOriginalBytesBase64。recordRows 按原文件顺序 rowIndex=0..n-1 保每物理 CSV 记录 rawRowBase64（含原行终止符）、CSV解码三个原 string 字段 pathField/digestField/sizeField 及 lineEnding；CSV引用可能包含换行，所以以完整CSV记录定义行，不能简单 splitlines 丢原字节。拼接所有 rawRow bytes 恰等解码原 RECORD bytes，原 bytes/hash 与 record 身份相符；不重写上级路径/空hash/空size/引号。raw数据绝不直接打开。

每 row 另记 installationRootId=approved-installation、normalizedInstalledPath、installedFileIndex、disposition/reason/ownerReview。实际按 RECORD 所在 dist-info 对应安装基准解析 pathField，再核真实批准环境根内规范路径；`../../../bin/tool` 只有解析结果确在批准环境根内且是实际普通文件才可映射，环境外逃逸一律拒绝、不改批准根兜底。原列不丢，规范路径不含 `..`。所有行都关联唯一 installedFiles；installedFiles.recordRowIndexes 与 row 双向一致（同一真实file多行必须显式归并理由且无规范名歧义）；RECORD自身也保，可按规范为该行空digest/size而recordSize=null，实际文件仍有真实bytes/SHA。

每file保 recordDigest（原hash字段或null）/recordSize（原size或null）/bytes/SHA/role、runtimeRequired、disposition/omissionReason/ownerReview/bundleMappings。bundled须至少一mapping且 omissionReason=null；非bundled须非空owner审过理由与实际ownerReview，mapping为空且runtimeRequired=false；runtime必需不得omit/build-only。数据/metadata/license/NOTICE/COPYING 的mapping为实际 bundle file；archive code mapping 的path为容器真正外层普通file、container/closed archiveId/memberName/raw bytes/SHA 与完整TOC对应；directory映射archiveId/memberName均null。所有 bytes/SHA不能只检查声明而省原artifact、原installed、最终目录三账。

八库及build工具逐artifact→installed→RECORD→code/data/metadata/license 原字节闭合。licenses.sourceFile 是批准安装根中的实际原文件，bundleFile 是批准bundle根中的真实副本，obligationReview 是 owner 实际审核记录；classification/noticeObligationReview 是审查内容，不从版本、basename或METADATA License字符串猜许可证。Python、stdlib、bootloader、动态库、平台 runtime 的 sourceArtifacts/licenseSources、bundleFiles/licenses、noticeReview/obligationReview另列完整闭包；需要NOTICE/COPYING等须保完整原文本。无真实许可/分类/费用结论则记缺证，不能产 archive-code-source-bound。typed费用与库分类未决项不因schema存在消失。

## 7. CR-A4：收据顺序、无环与外部批准

有向顺序：既有 source/profile/工具 commits → 实际build/log/installed/archive/code见证 → 后置 provenance → 包外完整 directory manifest → 包外 build receipt → 实际过程 commit。provenance不含自己hash、最终目录hash或未来receipt/process hash；payload排自身。archive构建后插入普通data provenance不重建PYZ。directoryFiles 是最终普通file全集（含root exe与provenance），只普通文件；directoryManifest在包外列同一全集，无自身项。build receipt.schema是schema的批准副本身份，不是receipt自hash；外部manifest/receipt/validation均不进入被hash bundle目录。

build receipt 保原全部字段，但 runtimeValidation 固定 not-executed、runtimeEvidenceManifest 必须显式 null；approvalStatus 固定 unapproved-produced-evidence。root 对实际来源、工具、全见证和原owner接收另出可信批准记录，绑定既有 build receipt 原bytes/hash及composition/profile/externalEvidenceManifest，不能从包内boolean推批准。caller启动前核该外部授权来源和同一receipt/完整目录/exe/provenance及批准证据包（可消费root已审且全hash绑定的固定包，但必须亲核包身份）。无批准/缺证/任一差异不得launch；probe不读此记录、不自证approved。

E1/E2以后后出 validation receipt 绑定既有 buildReceipt（approved-witness内原收据）及 approvedBuildRecord、完整runtimeEvidenceManifest；绝不回填原build receipt/provenance/旧directory。每个run依consumer合同CR-R保真实stdout/stderr/header/terminal/exit/signal与可用性、ordered runs/selector/mode/实际argv；source与frozen/parent的声明域按CR-H分别处理。完整成功采集仍要求Python域、23模块/第四模块/四函数/checker真实loader及fresh/cold/warm原件；失败只保实际已观察值，不能填批准预期值或剔除失败。完整manifest列所有raw输出与comparison文件，hash关系先原件后manifest后validation；不得在manifest收自己或validation，不把validation hash回写任何祖先。

runtimeValidation=collected-pending-comparison 时 comparison.state=pending，comparatorSource/oracleSource/comparisonReport/三结果均null；runtime manifest及完整runs仍非null且不可缺。runtimeValidation=compared 时 comparison.state=compared，comparatorSource/oracleSource/comparisonReport均非null、hash绑定真实独立来源；三个结果都是实际boolean，可false。compared仅表示比较发生，matched/equivalence/original operation三判独立。fullSuiteCollectionComplete=true要求selector=full-v1且全417有序完整terminal；collectionComplete=true仅所选采集完整。exit0不能覆盖header mismatch、unknown、缺行或oracle失败；missing-context/not-executed不能升级originalOperationPassed。caller分别报告，不让probe签后三判。

## 8. 原验收、失败与后继边界

full-v1完整417/320 datasets/83数学/106操作/54checks/50产品上下文保留；source/独立artifact/parent分别全量采集、全结构比较，再各自独立oracle。source=package不是正确性。BNode仅图同构，ordered rows/多重行/词法/None/ASK/SHACL六字段/typed/wire/payload/definitions/source/allocation/DAG/root/失败诊断均保。只预先列 runID/time/真实locator/编译域元数据允许分域；不一般删除变化字段。T05新实现限定收件不替allocation/日期首码、费用和库分类独审；本草案未读新oracle不判actual通过。

另12 B1 fresh trial=source/包×1×/10××3，四ontology图22/184；十ontology28/190仅full另案，两个B1 selector不拼full。原12 S1真实SQLite snapshotLoad独立HOLD，不以数组/0秒或旧storage_probe替换。parent package:dir/原入口/guards不由独立artifact替代。57P0/C–G/PRD10–12/六迭代、SQLite损坏输入HOLD、wholeH/owner及被拒物理方法、正式Job/Store/selected、指定同版双模型/CI/两OS干净无系统Python/断网/签名安装/真人/develop远端门原义保留，R7票独立不借。

失败保第一原件、候选/命令/输入身份/完整stdout-stderr/真实exit-signal；修订新candidate/delta复核，不能覆盖Fail或偷偷重试/安装/放宽cap。build缺证不产accepted provenance；未知异常INTERNAL_ERROR/exit1/incomplete，安全码不泄路径/堆栈/原值。完整actor/exactcodes见field-responsibility及consumer合同。

本窗只做普通Git/文件、stdlib JSON/哈希/TOML/有限关系及已有Prettier文档检查；无已命名获准离线JSONSchema引擎，本轮未探依赖环境、未安装、未网络。结构/refs/有限关系自检不是JSONSchema引擎验证，更不证明build/runtime。未执行产品/probe/builder/spec/reader/helper、prepared旧staticverify/generator、产品fixture模拟/pytest/业务compile/pycompile/archive解码、安装/版本能力探针/DB/native/GUI，未读旧binary/toolSDKwitness。examples全部synthetic design data，不能冒实际见证。作者写完停止，等待原T03全文读/owner接收和后续commit后fresh独审；不stage/commit/push/merge。

## 9. CR-R / CR-H：实际失败与精确header

完整规则以 consumer-contract.md §5–6 和 runtime-header.schema.json 为准。后继receipt版本为i05-runtime-validation-receipt/3；build provenance和build receipt均为本目录/3版本，build receipt永久not-executed/null，不回填。四份schema各自完整且final/delta manifest绑定原字节，header定义不是等待D2自行决定的空缺。D2只实现已审固定协议。

失败收据与成功采集分离：not-started、pre-header-rejected、incomplete、collected；header/terminal均区分absent/malformed/parsed，原bytes和真实exit/signal保留。所有required字段保持存在，未观察值显式null或实际部分集合；observedPaths绑定实际已观察的非null叶值，false是已观察值，不能改null吞掉。成功分支仍严格完整23+单列第四模块+四函数/checker、同代码域、exact三argv及完整417/单B1。坏Python域/非CodeType/alias/checker反例保真实值，不借“schema成功”升级运行结论。

source不读frozen provenance或包外批准/编译器文件：header中的declaredCompositionRef/provenanceRead/declaredPython固定null，declaredSupplierSources只有前22批准供应声明；23 actual source/loader及第23实际source observation交caller外部组合绑定。frozen/parent声明实际读取的唯一provenance原bytes/SHA与组合及其完整Python声明，caller对原build receipt复核。header.observedPython只含可由运行解释器观察的域，外部compilerExecutable/dontInherit保在declaredPython及caller收据，不作为probe包外读取指令。

## 10. CR-S26：依赖全集、版本与独立parent前置

dependency-specification.json逐26标准名保精确版本、profile/mapping完整原block、所有registry/markers/extras/workspace/dev/build字段和全平台wheel/sdist URL/hash/size/upload-time。六直接项恰defusedxml0.7.1、et-xmlfile2.0.0、openpyxl3.1.5、pyparsing3.3.3、pyshacl0.30.1、rdflib7.6.0。未来真实pyproject与lock中engine dependencies/metadata.requires-dist必须逐项同六项。共有包优先profile原block，三XLSX新增取mapping原block；engine合成metadata须另授实际resolver/锁维护窗口，不把原block拼接当真实锁。保rdflib[html]→html5rdf、openpyxl→et-xmlfile、全部平台marker和tools；不得删依赖凑23或擅自升级/改artifact来凑26。

26是完整workspace/dev/build/全平台package记录，23是canonical actual/frozen，22是source供应声明，8是专用semantic distributions，33是专用source inputs。六直接项不等八runtime；额外XLSX锁来源不自证安装、collect进专用artifact或许可证。实际artifact/METADATA/RECORD/LICENSE/NOTICE/COPYING和obligation/classification在E0获准后逐项补证，当前全部licenseApproved=null。任何新resolver/marker/extra/artifact差异须保首错、完整delta并重收，不得借本设计预签。

新parent/default58必须有独立parent guard/profile、完整依赖/runtime/许可闭包和root批准；不能在semantic33 provenance中混58源、把8改11或借semantic receipt证明wholeparent。guard-adoption-matrix完整58逐owner账保9冲突=2依赖+7源资源、21old-only/new-only11、mapping4；actualApprovedPin等保持null。历史独立根保23包旧源45 guard及原83入口；新semantic33、新parent58分别获批源/输出/env根并明确caller选择。任何owner兼容供pin、旧83/默认/原flags迁移回归缺失均阻断parent build eligibility，不阻断对其它纯规范逐项审查。

## 11. 前向采用、接口与文档验证边界

schema-change-index.json穷举14处版本literal及title/comment描述元数据delta；除此全部四schema节点逐值同旧D0。field-responsibility保全部1241 pointer、required、type、enum、$ref及actors/exactCodes，只同步10处shape.const、format/4与3.0.0规范链接。profile新增26/23/22/8/33计数及三scope源账；新descriptor与schema/collector必须在被依赖前具有实际固定Git/bytes/hash并获精确接收，本文和candidate manifest不充当授权签名或运行批准。

source declared22与actual23、frozen23与新consumer pin、header/2嵌入receipt/3、lock/dependencyRef两账、四writer和toolchain/root信任映射全部同版。任何old-v2 approval/Pass、旧profile配新锁、旧consumer2cf SHA冒新码均拒绝。I05业务carrier G02/G03的实现、schema字段与本项目独立新版本采用由其owner提交，本目录只精确列接口依赖，不代其定义或抢写。

本目录附有限synthetic设计反例与stdlib文档检查；不运行产品或import产品、不执行旧probe/collector/helper。有限shape/关系/字段/源集合与原hash检查不是离线JSONSchema2020-12引擎认证，也不是resolver/安装/compile/archive/loader/runtime/业务证据。旧D0/旧Fail/旧清单全部不改，新规范fresh独审与总控精确采用之前保持未采用。
