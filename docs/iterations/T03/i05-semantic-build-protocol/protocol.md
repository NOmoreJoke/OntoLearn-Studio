# T03 I05 semantic build protocol v2.0.0

2026-10-22。本完整 D0 草案将已收 adoption A1–A4 与 N-01 落为三个新 schema、完整 profile、consumer 合同和字段责任表。作者拟稿待原 T03 全文接收、实际 candidate commit 后 fresh 独审；无真实 build、安装、composition 或 runtime 实例。descriptor 的批准字段固定 null/空、executionAuthorization=false。原 offer47/adoption12 字节冻结；此处新版本不追改历史，不使原 v1 schema 可直接实施。

## 1. 固定输入、版本和采用方式

固定 base `bba31be7384a676e54cb3b64e219f14bf2a9460e`；branch `docs/T03-i05-semantic-offer-owner-review`。旧 offer candidate `6ba273a892b18a5ebaedc07aea6f36584999adcf`，process `21f9d4d288e8bd462b2252018578590110c08691`；本协议完整保留其字段能力，显式替换 archivePath/loaderCode 的歧义表示并增加原始 RECORD、批准根、第四模块和独立 validation receipt。新 JSON 的 exact path、bytes、SHA 由包外 draft-manifest 给出；本文件不预填未来自身 commit/hash。原 T03 接收后采用的 candidate/process 另由 owner 外报。

本目录规范对象如下；JSON Schema2020-12 shape 与本文/consumer-contract 的所有关系共同构成协议，任一不满足即拒绝。schema 不能表达的实际对象、路径、引用及证据真实性规则不能忽略。

| 文件                                   | 版本 / ID                                                                           | 用途                                    |
| -------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------- |
| build-provenance.schema.json           | i05-source-package-parity-build/2 / urn:ontolearn:i05:source-package-parity-build:2 | E0 后置包内构建声明                     |
| build-receipt.schema.json              | i05-build-receipt/2 / urn:ontolearn:i05:build-receipt:2                             | E0 包外 immutable build receipt         |
| runtime-validation-receipt.schema.json | i05-runtime-validation-receipt/1 / urn:ontolearn:i05:runtime-validation-receipt:1   | E1/E2 以后另出的 runtime receipt        |
| profile-descriptor.json                | i05-semantic-build-protocol-profile/2                                               | 完整未批准 profile，原 pin 为历史基线   |
| consumer-contract.md                   | 2.0.0                                                                               | I05 source/frozen 与 caller strict 合同 |
| field-responsibility.json              | 2.0.0                                                                               | 全字段 pointer 索引、actor/安全码/exit  |

新 schema 在 docs 中存在不授权产品读取；D2 须另明确精确采用路径/hash、consumer guard 与新第23 source pin。D1/D2/D3/E0 后分别开窗。旧供应22、T01四资源、I05资产保持原维护者；T03唯一四 writer 和锁未修改。本协议不重审新的 T05 oracle；当前口径是 T05 实现已限定收件，allocation delta 另审，旧 adoption 时点“未收件”只为历史。

## 2. CR-S：strict shape、集合与引用闭包

所有 schema 对象 additionalProperties=false；required 中每项必须存在。null 仅在 schema 显式允许处合法，不能用字段缺失替代 null，也不能用 null/unknown/空字符串冒必需实际证据。UTF-8 原字节、无 BOM、无 duplicate key（所有嵌套对象）、无 NaN/Infinity、无尾数据；布尔不是整数。source/payload/receipt hash 是64小写hex，ref/blob是40小写hex；SHA 算原字节而非重序列化，base64 算原字节。外部读者必须按有限精确 schema 而非 permissive object 接收。

`inputs.modules` 与 `moduleBindings` 恰23唯一 canonical 名/路径，顺序为 profile.canonicalModules；前22为6891供应，最后为经 D2 新批的 consumer，原2cf只祖先。`bindingId` 恰 `canonical:` 加 canonicalName。sourceCompilation.source 与相应 inputs.modules 的 ref/path/bytes/SHA/gitBlob 全同，Git source 不能转 installed 域；role 前22=canonical-module、最后=canonical-probe。bootstrap 是独立 `bootstrap-main`，不计入23。distributionCodeBinding 恰 `distribution:pyshacl.validator` / canonicalName=pyshacl.validator / role=distribution-module，不计入23。

四 function 名集合恰 semantic.reason、semantic.query、semantic.validate_shacl_text、Validator.run。前三 moduleName=ontolearn_engine.semantic、moduleBindingId=canonical:ontolearn_engine.semantic；第四 moduleName=pyshacl.validator、moduleBindingId=distribution:pyshacl.validator。不接受重复/缺项、同数异名或 dangling binding。每个 function.sourceCompilation 是其 module binding 同一 source/完整模块 compile 见证，不能换另一份源。所有 codeConstIndexPath 是实际记录的非空 co_consts 索引；同一数组分别在 source-compiled module 和 actual archive-extracted module 上逐步取 exact CodeType，再分别求 expectedFunctionCode/actualArchiveFunctionCode。每一步不是 exact CodeType、索引越界、反射 name 猜取、复用 sourceSHA 作 code 均拒绝。

inputs.resources 恰 profile 四 source，assets 恰两 source，pyproject/lock 与批准 dependencyRef 同源，writers 恰四路径 pyproject/uv.lock/build-engine.mjs/entrypoint.py（pyproject与lock两账全字段相同）。23+4+2+4 共33不同路径；profile/工具元数据另外列、不混计33。33项 before/after clean/bytes/blob/ref 须真实核同；AGENTS保护M不属于构建输入变更。profile 名/target/onedir/_internal/optimize=0/flag 固定，parent 原默认/旧 flag/43 guard 保留。新 profile 只按完整有限表解除 rule_revalidation exclude，其余 exclude 与 collectAll/hiddenImports/copyMetadata 逐项按完整 descriptor 精确集合；不得 collect-all engine/quality 或 glob contracts/v2。

八 distribution 名集合固定 rdflib7.6.0、pyshacl0.30.1、pyparsing3.3.3、owlrl7.6.2、prettytable3.18.0、wcwidth0.9.2、html5rdf1.2.1、packaging26.3。每项 name/version/selectedArtifact 与实际批准锁同一条目，不能只比八个数量。完整23包锁（workspace/dev/build-tool/marker/extra/全平台wheel与sdist）由外部 source/witness 绑定；每个 distribution.allPlatformArtifacts 列该包完整 lock artifacts，selectedArtifact 必须恰为其中一件并符合真实平台/marker。requiresDist/activatedExtras/markerEnvironment 保实际完整值，不因未激活marker删原项，rdflib[html]→html5rdf不得漏。buildToolDistributions 保完整同形来源/RECORD/许可和实际工具身份；build工具不强制混入八runtime集合。现有版本是设计目标，不是实际安装事实。

## 3. CR-A1：固定根域与真实普通文件

schema 的 root 是字段定义中的 const，实例不能任选根。所有最终普通文件（receipt.directoryFiles/executable/embeddedProvenance、runtimeComponents.bundleFiles/licenses、distribution license.bundleFile、bundleMappings.path 的实体、dynamicChecker.bundleFile、archive.location.file）固定 bundle-root。payloadFiles 固定 meipass-root，恰 `_internal` 下所有普通文件、排唯一 provenance；不是 bundle 根列表。Git source 根、approved-installation、approved-artifacts、approved-witness、approved-logs 分域；evidenceRoots 中是封闭 ID，root 的外部 approvalRecord 才把这些 ID 绑定到获准真实环境与前缀，不在包内放任意绝对 locator。

同一 data 文件两账必须 `bundlePath = "_internal/" + payloadPath` 且 bytes/SHA 全同；也须存在 receipt.directoryFiles 同一项。checker 根路径固定 `_internal/contracts/python/contract_v2.py`，payload 对应 `contracts/python/contract_v2.py`。唯一后置 provenance 根路径 `_internal/provenance/i05/source-package-parity-build.json`，payload 排除 `provenance/i05/source-package-parity-build.json`。四资源、两资产、lock 的 meipass 路径是 descriptor 唯一固定白名单，无 fallback。

executable.path 是根 `ontolearn-semantic-parity` 或 Windows 的 `ontolearn-semantic-parity.exe`（由批准目标OS唯一决定，不是两个副本）；root directoryFiles 中恰同一真实启动文件。runtimeComponents 必须分别保 python、stdlib、pyinstaller-bootloader 和实际 dynamic-library/platform-runtime；不能以 enum count 冒闭包。bootloader.bundleFiles 必含同一个 receipt.executable，path/bytes/SHA全同；不造 `_internal` 同名文件，不把 PE/Mach-O 片段伪成普通文件。确需片段见证须另批准布局 delta。

path 语法只第一层：拒绝空、绝对、反斜杠、drive/UNC、NUL、URL/冒号、`!`表达式、空/`.`/`..` segment、尾slash/点/空格。外部核验还拒绝 casefold/Unicode normalization/平台保留名/短名等别名、重复规范名、symlink（包括链中任一段）、hardlink 身份别名与根外 escape。root/caller 在获准根中实际 containment 与 lstat/真实普通文件核验；不能照字符串拼命令。包外 evidence 不进入最终 bundle 根；不为 nested PYZ 造普通文件。数据 raw RECORD 的原 pathField 不受安全 locator pattern 改写，因为它只是证据。

## 4. CR-A2：封闭 archive 账、第四函数与 raw witness

archiveId 唯一并仅可 carchive-main、pyz-main、external-pyc-main。location 是严格 oneOf：只有 file 或只有 parentMember；不准两者、空对象、任意字符串链/URL/cwd。carchive-main 必为 kind=CArchive、location.file=同一 root executable，archive bytes/SHA与该实体全同；depth=1。pyz-main 必为 kind=PYZ、parentMember.parentArchiveId=carchive-main、exact memberName/raw bytes/SHA与父完整 inventory 同一行全同；depth=2，无 file。external-pyc-main 只有经 root 批准 descriptor exact toolchain/布局时可用 kind=external-pyc/location.file 的实际普通文件，depth=1；它不能替代必需 canonical PYZ项。本未批准 descriptor 没有授权任何实际 external-pyc。

父必须先出现、唯一、无环、depth≤2；本版本禁止 PYZ 内再嵌 archive。complete TOC 保实际顺序、所有 name/kind/raw bytes/SHA，不只收23相关项；每容器 inventory 名唯一。actualArchiveCode.archiveId 必引用现存账项，memberName/memberKind/rawMemberBytes/SHA须与该容器 inventory 精确相符。每项 rawWitness 是 approved-witness 下真实解码/提取原字节保存件，同 raw hash/bytes；它与 final bundle 普通文件是两账，不能加入 directoryFiles 伪装。extractorSource/extractionMethodVersion 必绑定批准工具源码及真实运行身份。

23 canonical.actualArchiveCode 必是 pyz-main/PYZ-module 的真实 code；bootstrap.carchiveScript 是 carchive-main/CArchive-script，最早 main guard 在类发行前转 canonical main，canonical 对象唯一。第四函数单列 pyshacl.validator installed source→selected pyshacl artifact→RECORD row→实际 PYZ-module→same co_consts path function，不能用全TOC里一个名字代模块 code binding。module codeEqual / bootstrap codeEqual / function codeEqual 都须逐完整 fingerprint 真等，不接受人为 true。actual 工具若产生超此形态（如额外容器/层次/代码变换）先报确切版本/布局 delta，保首错与全TOC，由 D0/D3 修订后重审；既不总拒绝规避必需功能，也不自动开放递归 locator。

## 5. CR-C：checker 与 Python/code 域拆句（A2.5/N-01）

E0 对23 canonical、bootstrap、四函数，分别比较批准 source compile 与实际 archive 提取的 exact CodeType 指纹。

E0 对 checker，只比较批准 Git source 与实际 bundle data 原 bytes/SHA，并对二者分别 source compile 得 sourceCompilation.fingerprint 与 expectedBundleSourceCode。dynamicChecker.stage 固定 build-source-to-bundle-data-only；其 codeEqual 仅这两项完整指纹相等。checker 不要求进入 PYZ，构建声明不存在 runtimeLoaderCode。真正 resources.CONTRACT loader 的 get_code/对象/cache 是 E1 runtime receipt 的 dynamicChecker.runtimeLoaderCode，由 caller/header 回绑。

唯一 objectAuthority 是原 resources.CONTRACT；spec/name/origin/实际 loader 与消费者引用须核同。原 sys.modules 无此注册、registrationRequired=false，不能因此另exec、增加 alias、重注册或改公共 resources.CONTRACT。checker 顶层只读 schema/registry/errors，resources 另读 registry/lock；允许 semantic_identity、普通error目录及 validate("error", value)。不调用 resource_manifest/build_request/execute_request/derive_dependencies/permits_transition，不读 dependencies/states/fixtures 等额外 v2。

fingerprint 严格保原四字段 algorithm/sha256/pythonCacheTag/domain，domain 原字面仍保以兼容算法返回shape；真实域由 sourceCompilation/actualArchiveCode/expectedBundleSourceCode/runtimeLoaderCode 外层位置决定，不能凭 domain 字样冒 runtime 事实。algorithm=i05-code-object-marshal-filename-normalized/1，exact CodeType 递归 co_consts 中 code 只 replace co_filename=<i05-canonical-code>，保字节码、flags、name、qualname、lineno、linetable、exception table、所有常量及其他字段；marshal.dumps(...,4)→SHA256。不删除字段消差，不拿 sourceSHA/raw archive SHA 填 code fingerprint。

source compile=批准原bytes、实际source路径、exec、dont_inherit=True、optimize=0，使用实际构建解释器；compile不是执行 source。Python完整 implementation/version/hexversion/buildIdentity（versionString/buildNumber/date/compiler/apiVersion）/cacheTag/magic/marshal/optimize/byteorder/abiflags/platform/architecture/flags/compilerExecutable 全部保留。每 compile/archive/runtime 的 build/cacheTag/magic/flags/optimization和算法须同域；相同cacheTag不足。codeDomain.marshalReferenceStability=measured-same-domain 在E0只指 sourcecompile↔archive 的实际测量，不预签 E1 loader。E1独立 fresh/cold/warm/cache 重复 get_code 与真实 function.**code**，exact CodeType/相同canonical对象/稳定指纹逐项保见证；缺get_code、非exact类型、缓存/引用intern导致差异保首错，新算法版本/source/consumer/schema/工具共同delta后重审，不降sourceSHA。

## 6. CR-A3：RECORD、许可与 runtime 保全

distribution 与 buildToolDistributions 都保 selectedArtifact/allPlatformArtifacts、完整 METADATA/Requires-Dist/extras/marker environment、record原文件与recordOriginalBytesBase64。recordRows 按原文件顺序 rowIndex=0..n-1 保每物理 CSV 记录 rawRowBase64（含原行终止符）、CSV解码三个原 string 字段 pathField/digestField/sizeField 及 lineEnding；CSV引用可能包含换行，所以以完整CSV记录定义行，不能简单 splitlines 丢原字节。拼接所有 rawRow bytes 恰等解码原 RECORD bytes，原 bytes/hash 与 record 身份相符；不重写上级路径/空hash/空size/引号。raw数据绝不直接打开。

每 row 另记 installationRootId=approved-installation、normalizedInstalledPath、installedFileIndex、disposition/reason/ownerReview。实际按 RECORD 所在 dist-info 对应安装基准解析 pathField，再核真实批准环境根内规范路径；`../../../bin/tool` 只有解析结果确在批准环境根内且是实际普通文件才可映射，环境外逃逸一律拒绝、不改批准根兜底。原列不丢，规范路径不含 `..`。所有行都关联唯一 installedFiles；installedFiles.recordRowIndexes 与 row 双向一致（同一真实file多行必须显式归并理由且无规范名歧义）；RECORD自身也保，可按规范为该行空digest/size而recordSize=null，实际文件仍有真实bytes/SHA。

每file保 recordDigest（原hash字段或null）/recordSize（原size或null）/bytes/SHA/role、runtimeRequired、disposition/omissionReason/ownerReview/bundleMappings。bundled须至少一mapping且 omissionReason=null；非bundled须非空owner审过理由与实际ownerReview，mapping为空且runtimeRequired=false；runtime必需不得omit/build-only。数据/metadata/license/NOTICE/COPYING 的mapping为实际 bundle file；archive code mapping 的path为容器真正外层普通file、container/closed archiveId/memberName/raw bytes/SHA 与完整TOC对应；directory映射archiveId/memberName均null。所有 bytes/SHA不能只检查声明而省原artifact、原installed、最终目录三账。

八库及build工具逐artifact→installed→RECORD→code/data/metadata/license 原字节闭合。licenses.sourceFile 是批准安装根中的实际原文件，bundleFile 是批准bundle根中的真实副本，obligationReview 是 owner 实际审核记录；classification/noticeObligationReview 是审查内容，不从版本、basename或METADATA License字符串猜许可证。Python、stdlib、bootloader、动态库、平台 runtime 的 sourceArtifacts/licenseSources、bundleFiles/licenses、noticeReview/obligationReview另列完整闭包；需要NOTICE/COPYING等须保完整原文本。无真实许可/分类/费用结论则记缺证，不能产 archive-code-source-bound。typed费用与库分类未决项不因schema存在消失。

## 7. CR-A4：收据顺序、无环与外部批准

有向顺序：既有 source/profile/工具 commits → 实际build/log/installed/archive/code见证 → 后置 provenance → 包外完整 directory manifest → 包外 build receipt → 实际过程 commit。provenance不含自己hash、最终目录hash或未来receipt/process hash；payload排自身。archive构建后插入普通data provenance不重建PYZ。directoryFiles 是最终普通file全集（含root exe与provenance），只普通文件；directoryManifest在包外列同一全集，无自身项。build receipt.schema是schema的批准副本身份，不是receipt自hash；外部manifest/receipt/validation均不进入被hash bundle目录。

build receipt 保原全部字段，但 runtimeValidation 固定 not-executed、runtimeEvidenceManifest 必须显式 null；approvalStatus 固定 unapproved-produced-evidence。root 对实际来源、工具、全见证和原owner接收另出可信批准记录，绑定既有 build receipt 原bytes/hash及composition/profile/externalEvidenceManifest，不能从包内boolean推批准。caller启动前核该外部授权来源和同一receipt/完整目录/exe/provenance及批准证据包（可消费root已审且全hash绑定的固定包，但必须亲核包身份）。无批准/缺证/任一差异不得launch；probe不读此记录、不自证approved。

E1/E2以后后出 validation receipt 绑定既有 buildReceipt（approved-witness内原收据）及 approvedBuildRecord、完整runtimeEvidenceManifest；绝不回填原build receipt/provenance/旧directory。每个run保真实stdout/stderr/header/terminal/exit/signal，ordered runs/selector/mode/argv、同composition/provenance digest、Python域、23模块/第四模块/四函数/checker真实 loader 和fresh/cold/warm原件。完整manifest列所有raw输出与comparison文件，hash关系先原件后manifest后validation；不得在manifest收自己或validation，不把validation hash回写任何祖先。

runtimeValidation=collected-pending-comparison 时 comparison.state=pending，comparatorSource/oracleSource/comparisonReport/三结果均null；runtime manifest及完整runs仍非null且不可缺。runtimeValidation=compared 时 comparison.state=compared，comparatorSource/oracleSource/comparisonReport均非null、hash绑定真实独立来源；三个结果都是实际boolean，可false。compared仅表示比较发生，matched/equivalence/original operation三判独立。fullSuiteCollectionComplete=true要求selector=full-v1且全417有序完整terminal；collectionComplete=true仅所选采集完整。exit0不能覆盖header mismatch、unknown、缺行或oracle失败；missing-context/not-executed不能升级originalOperationPassed。caller分别报告，不让probe签后三判。

## 8. 原验收、失败与后继边界

full-v1完整417/320 datasets/83数学/106操作/54checks/50产品上下文保留；source/独立artifact/parent分别全量采集、全结构比较，再各自独立oracle。source=package不是正确性。BNode仅图同构，ordered rows/多重行/词法/None/ASK/SHACL六字段/typed/wire/payload/definitions/source/allocation/DAG/root/失败诊断均保。只预先列 runID/time/真实locator/编译域元数据允许分域；不一般删除变化字段。T05新实现限定收件不替allocation/日期首码、费用和库分类独审；本草案未读新oracle不判actual通过。

另12 B1 fresh trial=source/包×1×/10××3，四ontology图22/184；十ontology28/190仅full另案，两个B1 selector不拼full。原12 S1真实SQLite snapshotLoad独立HOLD，不以数组/0秒或旧storage_probe替换。parent package:dir/原入口/guards不由独立artifact替代。57P0/C–G/PRD10–12/六迭代、SQLite损坏输入HOLD、wholeH/owner及被拒物理方法、正式Job/Store/selected、指定同版双模型/CI/两OS干净无系统Python/断网/签名安装/真人/develop远端门原义保留，R7票独立不借。

失败保第一原件、候选/命令/输入身份/完整stdout-stderr/真实exit-signal；修订新candidate/delta复核，不能覆盖Fail或偷偷重试/安装/放宽cap。build缺证不产accepted provenance；未知异常INTERNAL_ERROR/exit1/incomplete，安全码不泄路径/堆栈/原值。完整actor/exactcodes见field-responsibility及consumer合同。

本窗自检仅普通Git/文件、stdlib JSON/AST/re/数学和已有Prettier；无已命名获准离线JSONSchema引擎，本轮未探环境、未安装、未网络。结构/refs/有限关系自检不是JSONSchema引擎验证，更不证明build/runtime。未执行产品/probe/builder/spec/reader/helper、prepared旧staticverify/generator、产品fixture模拟/pytest/业务compile/pycompile/archive解码、安装/版本能力探针/DB/native/GUI，未读旧binary/toolSDKwitness。examples全部synthetic design data，不能冒实际见证。作者写完停止，等待原T03全文读/owner接收和后续commit后fresh独审；不stage/commit/push/merge。
