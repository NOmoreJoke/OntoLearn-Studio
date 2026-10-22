# I05 source/frozen consumer contract v2.0.0

本件是 D0 完整消费合同；与 protocol.md、三个完整 schema、profile-descriptor 和 field-responsibility 共同生效。未实现 consumer；2cf frozen 仍有原总拒绝，不能以本件称其通过。D2 原 I05 owner 另窗实施新LOCK/八dist、strict读取和新第23 pin，T03/root随后审真实 composition。descriptor目前 approvedConsumerPin、approvedDependencyPin、approvedToolchain、acceptedCompositionRef、approvedProtocolRecord、approvedEvidenceRootRecord=null，approvedWrapperPins=[]，executionAuthorization=false；所有这些都不是actual可运行批准。

## 1. 启动输入是三个 exact argv

canonical main 接收且只接收以下三数组（不含可执行路径）：

```json
[
  ["--semantic-source-package-probe", "full-v1"],
  ["--semantic-source-package-probe", "b1-semantic-1x-v1"],
  ["--semantic-source-package-probe", "b1-semantic-10x-v1"]
]
```

source 调用 `python -m ontolearn_engine.semantic_source_package_probe` 加该数组；独立 frozen 调 root真实executable加该数组；parent新flag仅原样转 canonical main。单flag、unknown selector、额外参数、flag=value、任意path/环境/receipt参数全以前置exit2拒绝，不落parent默认入口；其他已批旧flag/default原义保留。无通用locator入口，不从stdin读取业务，获准caller stdin=/dev/null。此处不另造argv错误安全码，保原consumer现有受限诊断/exit2；新增code逐项在第4节，不能擅改公共errors catalog。

## 2. strict解析与顺序

caller在启动前从root批准固定外部根核批准记录→原build receipt→完整当前directory/provenance/exe→全hash绑定证据包；source模式另核实际checkout与批准pin。不能只信一条摘要或包内自报approved。失败保持not-started，不能先launch再补批准。所有外部locator只由caller/root按固定域读；probe从来不读Git对象/owner接收/profile原件/log/artifact/原安装环境/RECORD原路径/包外收据或witness，不做网络、archive解码或额外exec。

frozen原有resource/lock/distribution/Python前门保留；唯一provenance路径是 `_MEIPASS/provenance/i05/source-package-parity-build.json`。最多读16MiB+1，>16MiB拒绝而不截断、流式半解析或增cap。UTF-8无BOM严格JSON，所有嵌套duplicate keys、nonfinite、尾数据拒绝；按exact version/strict schema全required/type/enum/const/refs，加protocol所有crossfield规则。unknown属性/缺字段/非法null/布尔作整数均拒绝。超cap的新完整映射须D0/D2显式新版本，不靠删字段消差；16MiB只是逻辑cap，不是CPU/native/wholeH许可。

声明核验包括：组合refs语法及声明关联（不代表root批准）；23唯一名称/源pin/role/moduleBindingId闭包、bootstrap和pyshacl.validator额外绑定；4资源/2资产/lock的精确固定路径与bytes/SHA；八dist名字/版本与Python/code域；所有bundle/data映射两根转换；archive封闭账、引用闭包/父子次序/无环/深度/TOC；RECORD数据 shape/逐行关系；completion无runtime预签；任何必需缺证无fallback。probe只核声明可由本域观测的关系，不解引用外部source/RECORD，外部真实性由root/caller核，二者不可互代。

source只读模块相邻probe_inputs两资产、checkout packages/contracts四资源、批准root uv.lock；frozen只读固定contracts四资源、provenance/i05/source-package-parity两资产、provenance/uv.lock及唯一provenance。声明中的source/log/installed/witness路径永远是数据；不根据它扩大probe读取白名单。包内manifest的runtime/许可映射由caller核完整目录；probe只在固定已批bundle域核必要映射，不能用其字符串读包外或新增v2资源。四资源之外的dependencies/states等不因schema引用可读。

实际import后、图业务调用前，probe核23 canonical name/spec.name/sys.modules[name]同对象、实际source/frozen origin/loader class、get_code返回exact CodeType与完整指纹；前三函数runtime.__code__绑定semantic模块，第四是pyshacl.validator.Validator.run真实对象，按实际source/archive见证同co_consts索引比较。checker只从resources.CONTRACT原对象取得实际loader code，核spec/name/origin与消费者同对象，不能再exec/alias或要求进PYZ。前置失败可已发生公共checker读取三JSON的import事实，报告不得写“未import任何代码”；只保证图计算尚未开始。缺get_code/错版/alias/code差异拒绝，sourceSHA不能顶替code。

source前22按已批原pin核actual source bytes→sourcecompile→实际loader；第23不嵌自己的SHA/descriptor/provenance hash，不把2cf旧hash硬写进新consumer。source输出actualSourceBytes/actualSourceSha256、实际loader fingerprint与代码域，由caller对新approvedConsumerPin核同；frozen对应source23来自外部批准composition的manifest声明、PYZ实际code与runtime loader，bootstrap另核。caller不认可未批准新source pin，probe不能自签。

## 3. header、完整终态与运行收据

header必须分开 declared supplier/source identity、actual模块/函数/checker runtime code、declaredCompositionRef、读取provenance原bytes/SHA、Python精确域、selector/mode。externalReceiptStatus固定external-unverified，packageCodeBoundToSource最多 archive-loader-consistent-with-declared-source；source23 actualSourceSha来自实际观察，不是内嵌自hash。未来D2精确header schema须同本合同；缺字段不能以日志文字替代。caller逐字段把header digest/ref/runtime code与启动前同一批准build receipt及见证回绑，不能exit0抵消差异，不让probe输出approved。

完整采集UTF-8 JSONL：唯一header→每条完整observation→唯一terminal。full-v1恰417有序；两个B1 selector各一measurement，不能拼full。所有真实stage结果/graph/query variables/全rows/None/ASK、reason图/SHACL六字段、typed全字段/payload/原bytes/base64/wire/source/definition/allocation/DAG/root/失败诊断保全。known rejection、unsupported、missing-context、not-executed分态，不补view或改业务pass；未知为INTERNAL_ERROR/incomplete。

原cap：descriptor1MiB、input8MiB、总9MiB、case≤512（actual417）、单item32MiB、stdout64MiB、terminal预留64KiB；120s monotonic每stage前后检查。完整item先预算再写。opaque native调用不能被逻辑deadline即时中断；hardkill的半行raw bytes仍保存/incomplete，exit记null及真实signal。cancel request/stopping/目标真实停止/readerjoin/引用释放分别记录，130只协作stop边界，不冒真实signal。未获得该运行窗时不启动任何微验或完整suite。

build receipt永久not-executed/null；后出validation receipt保buildReceipt原hash、外部approvedBuildRecord、完整runtime manifest和runs。collected-pending-comparison的comparator/oracle/report/三个结果显式null；compared时三身份非null且三个独立boolean可false。comparison report须覆盖完整受审scope，不能用full未完成的片段判full通过。sourcePackageEquivalent、externalOracleMatched、originalOperationPassed分别外部判；仅collectionComplete/fullSuiteCollectionComplete为采集状态。相同Python/cache/flags等code域不一致即拒绝，完整domain字段不能删；真实fresh/cold/warm/cache稳定性另E1。

## 4. actor、exact安全码与exit

| 主体/阶段             | exact code                          | exit / 终态                                |
| --------------------- | ----------------------------------- | ------------------------------------------ |
| T03 build输入         | BUILD_INPUT_IDENTITY_INVALID        | 实际build非零；不得产accepted provenance   |
| T03 build代码域       | BUILD_CODE_DOMAIN_MISMATCH          | 同上，保第一实际差异                       |
| T03 archive           | BUILD_ARCHIVE_INCOMPLETE            | 同上，保完整TOC/raw首错                    |
| T03许可映射           | BUILD_LICENSE_MAPPING_INCOMPLETE    | 同上，保缺证，不以unknown补齐              |
| caller批准缺失        | APPROVED_BUILD_RECEIPT_UNAVAILABLE  | not-started，无probe exit                  |
| caller外部来源        | APPROVED_SOURCE_BINDING_INVALID     | not-started，无probe exit                  |
| caller目录            | BUNDLE_DIRECTORY_MISMATCH           | not-started，无probe exit                  |
| probe缺provenance     | FROZEN_BUILD_PROVENANCE_UNAVAILABLE | 前置exit2，图业务未开始                    |
| probe strict格式      | BUILD_PROVENANCE_FORMAT_INVALID     | 前置exit2                                  |
| probe声明组合关联     | DECLARED_COMPOSITION_FORMAT_INVALID | 前置exit2，不称未批准的组合已批准          |
| probe资源关联         | BUNDLE_PROVENANCE_RESOURCE_MISMATCH | 前置exit2                                  |
| probe frozen code     | LOADER_ARCHIVE_CODE_MISMATCH        | 前置exit2                                  |
| probe code域          | CODE_DOMAIN_INVALID                 | 前置exit2                                  |
| probe checker对象     | DYNAMIC_CHECKER_IDENTITY_INVALID    | 前置exit2                                  |
| probe source code     | LOADER_SOURCE_CODE_MISMATCH         | 保既有source前置拒绝/exit2，不与frozen码混 |
| probe未知异常         | INTERNAL_ERROR                      | exit1/incomplete                           |
| caller header回绑     | HEADER_PROVENANCE_BINDING_MISMATCH  | 外部failed，保真实child exit/signal        |
| caller输出/终态不完整 | RUNTIME_EVIDENCE_INCOMPLETE         | 外部incomplete，保真实child exit/signal    |

安全输出只稳定code及受限stage/参数，不泄原路径、堆栈、凭据或业务原值。原resource/lock/dist/Python现有安全前门码保留，不虚称新码在2cf已实现。argv/asset/provenance前置非法exit2；unknown/harness/逻辑预算不完整exit1；exit0仅所选采集完整，可包含known rejection/missing-context/not-executed，非业务通过。external caller错误不能伪造成child exit2。build只有真实非零要求，本协议不编造统一数值exit；child signal保实际。所有首次失败不可覆盖，修复新candidate/delta再审。

字段责任全量见 field-responsibility.json：T03生产真实外部证据，root审批exact组合与原件，caller先核后绑，probe只strict声明和本域实际loader，不读包外locator、不自签批准。此分工不授权安装/build/运行/工具实现，也不代指定双方独审/CI/两OS/真人/develop和原B1/parent/S1/正式门。
