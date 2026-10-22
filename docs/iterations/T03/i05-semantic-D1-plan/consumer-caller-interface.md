# D2 / caller 接口与失败收据落地清单

此处列c3eb固定v2合同的完整协作验收面；26包组合后继实现必须另按forward-protocol-delta的v3/header2/receipt3精确升级全部映射，不能用旧version配新26锁启动。完整四schema、descriptor、protocol/consumer固定身份在readonly-input-manifest。字段名称、required/type/null/enum/unknown规则均以**完整固定schema**为准，不能用本清单覆盖或简化。D2/I05维护consumer；caller/root维护外部信任、运行原件、验签/绑定与validation；T03只协调四writer接口。

三scope guard关联见guard-scope-matrix/guard-migration-strategy：专用semantic33不变，拟parent/default58与历史45另有完整owner采用/旧profile83迁移门；caller必须按批准scope选择实际exe/root，不能把历史83报告当new417/header2或把9冲突两版bytes混用。

## 1. strict 入口与外部输入界限

D2后继先落 strict UTF-8 原字节解析：最大provenance16MiB，读取至cap+1判超限，不截断后解析；拒BOM、任何层duplicate key、NaN/Infinity、尾数据、unknown/missing字段、错类型、bool作为integer、非允许null、错误ref/hash大小写长度、越界/重复/逃逸路径。JSON Schema形状之外须实现CR-S/A1/A2/C/A3/A4/R/H全部关系。所有schema与exact已收采用身份由owner/root锁定，不能运行时任选schema路径或下载远程$ref。

source只读module旁两probe_inputs资产、checkout四contracts和根uv.lock；frozen只读对应四contracts/两assets/同lock/唯一provenance白名单。shape中的外部Git/source/安装根/ownerAcceptanceRecord/extractorSource/日志/receipt字段只是声明，不赋probe解引用权限。不得让probe读caller批准记录、外部witness/compiler/许可目录，不增加公网或任意文件白名单。

业务入口只接完整两项三数组：`["--semantic-source-package-probe","full-v1"]`、`["--semantic-source-package-probe","b1-semantic-1x-v1"]`、`["--semantic-source-package-probe","b1-semantic-10x-v1"]`。source用`python -m ontolearn_engine.semantic_source_package_probe`再加数组；frozen root exe加同数组；parent最早canonical分派同数组。invalid argv保原数组与受限stderr，exit2，不能扩大成功接收集合。

## 2. header 完整字段与分域

顶层字段**全部required**：kind、format、profileId、mode、selector、externalReceiptStatus、declaredCompositionRef、provenanceRead、declaredSupplierSources、declaredPython、observedPython、moduleLoaders、distributionModuleLoader、functionCodes、dynamicChecker、observedSource23、packageCodeBoundToSource、sourceCodeBoundToSource。exact值kind=header、format=i05-semantic-runtime-header/1、profileId=i05-source-package-parity-v2、externalReceiptStatus=external-unverified；probe无批准/验签true字段。

| 组                                                       | source                                                                 | frozen-independent / parent                                                    |
| -------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| declaredCompositionRef / provenanceRead / declaredPython | 显式null，不能读取frozen provenance补填                                | 来自唯一provenance原bytes/SHA及完整声明Python/组合；caller再核批准上下文       |
| declaredSupplierSources                                  | profile前22唯一有序canonicalName+完整source五身份；没有内嵌selfhash    | 等provenance.inputs.modules完整23唯一有序，source23为D2新批准实际pin           |
| moduleLoaders.actualSource                               | 23实际原bytes/SHA；每条绑定canonical:name                              | 全部null，不能把包内code指纹冒sourcebytes                                      |
| observedSource23                                         | 实际bytes/SHA/actualLoaderCode，等第23模块；caller外部核新pin          | null                                                                           |
| 两code绑定状态                                           | sourceCode最多loader-consistent-with-observed-source，packageCode=null | packageCode最多archive-loader-consistent-with-declared-source，sourceCode=null |

moduleLoaders每项完整键：bindingId/canonicalName/loaderClass/specName/origin/exactCodeType/singleCanonicalObject/runtimeLoaderCode/actualSource；distributionModuleLoader同形但独立pyshacl.validator。functionCodes每项name/moduleBindingId/runtimeFunctionCode/exactCodeType/codeConstIndexPath；四固定函数不能同数异名。dynamicChecker每项name/objectAuthority/sysModulesRegistrationRequired/loaderClass/specName/origin/runtimeLoaderCode/exactCodeType/sameConsumerObject；原对象仅resources.CONTRACT，registrationRequired=false，不新exec/alias/注册改变身份。

observedPython完整implementation/version/hexversion/cacheTag/magicHex/marshalVersion/optimize/byteorder/abiflags/platform/architecture/flags/buildIdentity；flags与buildIdentity每个required子字段按原schema全保。compilerExecutable和dontInherit不在header.observedPython，前者属于外部来源，二者仍在frozen declaredPython与caller run.python。run.python投影去这两项后必须逐字段等header.observedPython；不是只比较Python版本字符串或cacheTag。失败的非CPython/非3.12/优化非0等实际域允许保存，但不能标collected。

实际loader/CodeType/同canonical对象/四函数同co_consts路径/checker对象同consumer全部须真实观察，失败false/null/错fingerprint不能洗成预期true。bootstrap不计23；pyshacl.validator不计23。source compile、archive、runtime完整fingerprint algorithm/sha256/pythonCacheTag/domain保持原四字段，算法仅co_filename递归归一且其余code字段不变；D1不执行compile、marshal、get_code或native调用。fresh/cold/warm/缓存稳定性外部见证在E1真实取得，header不读取/生成包外locator。

## 3. caller 收据的每个 run 全字段

run **全部required**：runId、mode、selector、argv、stdout、stderr、header、terminal、actualExitCode、signal、collectionComplete、fullSuiteCollectionComplete、declaredCompositionRef、provenanceSha256、externalReceiptStatus、python、moduleLoaders、distributionModuleLoader、functionCodes、dynamicChecker、observedSource23、packageCodeBoundToSource、sourceCodeBoundToSource、observationState、headerState、terminalState、observationIds、observedPaths、failure、headerPayload、observationOutcomes。各值只按原schema和状态明确允许null/部分有序子集；字段缺失不是“未观察”。receipt module/checker额外freshColdWarmEvidence属于caller外部证据，不进入header。

| observationState    | raw/header/终态                                                                                                                                                                                          | exit/signal/failure与完整性                                                                                                                               |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| not-started         | 未dispatch；stdout/stderr/header/terminal/headerPayload、实际观察均null/空；observedPaths/observationIds=[]；header/terminalState=absent                                                                 | exit/signal=null；caller/prelaunch/既有三prelaunch码之一；两complete=false。拟argv不当已运行                                                              |
| pre-header-rejected | 真child；stdout/stderr两原件非null可0B；header/terminal absent且引用与payload=null；保已取得部分观察                                                                                                     | exit2/signal=null；probe前置错误；invalidargv phase=argv/reason=argv-rejected/code=null，引用真stderr；两complete=false                                   |
| incomplete          | 真child；stdout/stderr非null；header和terminal各自absent/malformed/parsed。absent引用null；malformed引用完整坏JSON/半行或strict shape非法原JSON，headerPayload=null；parsed引用非null且完整shape payload | 保实际exit；有真实signal则exit=null；未确认终态保真实null。failure保caller/probe、实际phase/code/reason/firstEvidence；两complete=false，保partial和false |
| collected           | header/terminal parsed非null且headerPayload完整；raw全保，23+独立第四模块+四function+原checker+Python/argv/域/绑定都满足                                                                                 | exit0/signal=null/failure=null；collectionComplete=true。full-v1恰417有序唯一项与outcomes，fullSuite=true；每B1仅1measurement且fullSuite=false            |

parsed仅表示shape可解析，错mode/selector/ref/digest/对象等actual header仍要保，run实际投影等原值，caller另记HEADER_PROVENANCE_BINDING_MISMATCH、incomplete。不能把header改成拟调用或批准值。shape不可解析则malformed、payload=null；不能修造一个可解析header替代原raw。headerPayload是原raw严格解析完整副本，raw文件原hash不能由重序列化替代。

observedPaths从run的python/moduleLoaders/distributionModuleLoader/functionCodes/dynamicChecker/observedSource23/declaredCompositionRef/provenanceSha256/两个绑定状态导出每个已观察非null叶值的JSON pointer全集；使用schema规定路径，不是随意mask。false、0、空string如实际允许值均不能因Python truthiness被吞。拒重复/越界/指向null/缺已观察叶值；无观察null/空list不列叶值。caller逐字段与raw/header/首错交叉核，不能同时改mask和值规避。此设计不等于实际raw已核过。

observationIds/outcomes等长顺序一致，outcomes只success/known-rejection/unsupported/missing-context/not-executed；它们只是原件索引，不替代完整graph/query/SHACL/typed/payload结果。known rejection等可采集完整但不推业务通过。每次尝试包括not-started均有序保留，不省首错。firstEvidence、malformed片段、stdout/stderr、header/terminal、fresh/cache/comparison全部列同一runtimeEvidenceManifest，原bytes/hash相等，无旁日志。

## 4. exact 安全码与真实 exit

| 维护者/阶段       | exact code                                                                                                                                                                                                                                                              | 真实记录规则                                                      |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| T03 build         | BUILD_INPUT_IDENTITY_INVALID / BUILD_CODE_DOMAIN_MISMATCH / BUILD_ARCHIVE_INCOMPLETE / BUILD_LICENSE_MAPPING_INCOMPLETE                                                                                                                                                 | 真非零，保首差；不编统一数字exit，不出accepted provenance         |
| caller prelaunch  | APPROVED_BUILD_RECEIPT_UNAVAILABLE / APPROVED_SOURCE_BINDING_INVALID / BUNDLE_DIRECTORY_MISMATCH                                                                                                                                                                        | not-started，无childexit；不假装probe前置拒绝                     |
| probe             | FROZEN_BUILD_PROVENANCE_UNAVAILABLE / BUILD_PROVENANCE_FORMAT_INVALID / DECLARED_COMPOSITION_FORMAT_INVALID / BUNDLE_PROVENANCE_RESOURCE_MISMATCH / LOADER_ARCHIVE_CODE_MISMATCH / CODE_DOMAIN_INVALID / DYNAMIC_CHECKER_IDENTITY_INVALID / LOADER_SOURCE_CODE_MISMATCH | 前置exit2，保source/frozen域与真实诊断；声明组合合法不等已批准    |
| probe unknown     | INTERNAL_ERROR                                                                                                                                                                                                                                                          | exit1/incomplete                                                  |
| caller postlaunch | HEADER_PROVENANCE_BINDING_MISMATCH / RUNTIME_EVIDENCE_INCOMPLETE                                                                                                                                                                                                        | external failed/incomplete，保真childexit/signal；不能覆写为exit2 |

D0既有resource/lock/dist/Python受限安全码保留，不能宣称2cf已实现上述新增码。稳定code与受限stage/参数可公开；真实原路径、堆栈、业务原值/凭据不混入安全stderr。未知异常/harness/逻辑预算不完整exit1；exit0只表示所选采集完整，不等三个业务结果为true。

## 5. 流、预算、收据顺序与外部比较

完整JSONL顺序是唯一header→逐条完整observation→唯一terminal。full-v1恰417原序，含320datasets、83math-input-context、106original-operations、54learning-checks、50product-cases；这些是不同计数维度不能相加误称用例总数。原graph/query变量/全rows/None/ASK、reason/SHACL六字段、typed全字段/payload/原bytes/base64/wire/source/definition/allocation/DAG/root/失败诊断都保全，不能仅保存hash或pass摘要。

原预算：descriptor1MiB、input8MiB、总9MiB、case≤512（actual417）、单item32MiB、stdout64MiB、terminal预留64KiB；120s monotonic每stage前后检查，完整item先预算再输出。opaque native不能承诺deadline即时中断；hardkill半行bytes照存incomplete。cancel request/stopping/真实目标停/readerjoin/引用释放分记，130仅协作stop边界，signal记录真实值。资源窗未授不启动微验、warming或完整suite。

E0有向链：既有source/profile/collector工具commits→真build/log/installed/archive/license/code→后置provenance→包外完整directoryManifest→buildReceipt→过程commit。provenance不写自身/未来receipt/hash，payload排自己；directoryFiles含最终唯一provenance与rootexe，不把raw archive witness伪成普通file。buildReceipt所有required按固定schema保留，runtimeValidation永远not-executed、runtimeEvidenceManifest=null、approvalStatus=unapproved-produced-evidence；root另出可信批准记录。

E1/E2另出runtime receipt，绑定既有buildReceipt原hash+approvedBuildRecord+完整runtime manifest，不回填旧buildReceipt/provenance/directory。manifest保全部现有原件完整不等suite通过。pending-comparison时comparison.state=pending且comparatorSource/oracleSource/comparisonReport/三结果全null；compared时三来源身份非null、报告真实、三结果分别boolean可false；scope失败或不完整不可用片段判full通过。未经新source23/consumer/外部caller审核，不能用D0模板、合成header/417 IDs或selfcheck结果当运行证书。
