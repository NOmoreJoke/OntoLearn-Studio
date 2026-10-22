# D2 业务 carrier R2：失败身份与 caller 原件

本件是 R1-F01/P2、R1-F02/P2 的最小纯设计修订，未获独审结论。revisionBase 为 `aefa82e51643e0a75ecb960645d63917b046edd6`。旧 D2 57 件、首候选及过程33件、R1独审22件、root receipt1件，共113件冻结。旧七规范、首失败与旧1241/header不原位修改。R2 完整文法见 `wire-grammar-r2.json`，全字段责任见 `field-map-r2.json`，旧15项mandatory材料与13族完整原值仍保留。

T03 完整 protocol/consumer3.0.0、profile4、header2、build/runtime receipt3 已由root限定设计接收，固定 `d9c3c151614674f2c7a6e3d7f6507aa7ba81db58` 的14件逐一current=Git=bytes/SHA；不是仍只收到D1五件方案。完整v3不自动接收本业务stream2或R2身份映射，actual pins继续null/空、executionAuthorization=false。费用R4六件纯提案在 `0f9d815c592bf434790c00c8ac6cc6de7a5fd3d8` 限定接收，仅补M06纯规范材料；不把提案per-ID输出当真实费用或业务golden。规范自身历史“待审”文字保原字节，采用状态以外部root acceptance为准。

## 1. 三个身份与完整失败分支

caller 在实际调度登记原件中产生并记录 `attemptId`，原顺序唯一；该身份须在child结果前已存在，不是为满足schema事后编字符串，也不是PID/issuer/权限。已调度但批准前停止的not-started也有真实caller登记项；它只证明未dispatch的调度尝试。每次真实dispatch独立attempt，不借重试覆盖首错。

`carrier.runId` 专指从严格接受的本次 child ContextFrame 取得的身份；header本身没有runId，header合法也不能代替context。未接受context时原坏行中即使有词法runId也仅保raw，不能升级身份。`binding.receiptRunId` 则是caller生成的外部receipt条目身份，按本新业务policy等于实际 `attemptId`；它不要求等于child runId。v3 `field-responsibility.json /propertyIndex/755` 明定receipt `#/properties/runs/items/properties/runId` 的producer=caller、externalVerifier=root/caller、probeDuty=not-read-external-receipt。schema仍为required非空string，R2不nullable化它。

| 实际情况                                               | carrier身份                                                                        | binding2.attemptCore                                                                                                | receipt3逐条对应                                                                                                                           |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 未dispatch                                             | `identityAvailability=not-dispatched; runId=null`，stdout/stderr/exit/signal均null | NotDispatchedCore保attemptId与not-started                                                                           | 同一真实caller attemptId作row.runId，CR-R not-started全required、实际null/空与原prelaunch失败；不造child                                   |
| 已dispatch，0byte、无header、坏header或尚无合法context | `unavailable-before-context; runId=null`，两完整raw FileRef非null，即使0byte       | PreContextFailureCore保attempt、实际mode/selector、完整双流、真实exit/signal、原header范围/失败与caller witness IDs | 仍有同序row.runId=attemptId；无context不影响caller条目身份。符合实际probe前置exit2才pre-header-rejected，否则incomplete。不能冒not-started |
| 已接受唯一context，之后完整或失败                      | `observed-context; runId=context.runId`非空                                        | BoundContextCore.core保同child runId、mode/selector/raw/实际header-terminal范围                                     | 外部row.runId仍为caller attemptId，通过binding明确连到child core；原CR-H实际header逐字段映射，不删中途失败/false/partial                   |

缺context而填child ID、存在context却填null/其他ID、将attempt/PID/expected当child、重复/未知context、dispatch冒not-started、丢0byte FileRef均拒绝。无context的terminal样字节只能保拒绝原件，不能造受信终态。accepted context之后的失败不清空其真实身份或早先stage。

## 2. receipt3 的完整双向投影

`receipt-projection-r2.json` 逐一列全31个run required键、received完整shape、owner、适用/未到达值与精确JSON pointer。所有真实caller登记项（含失败/未启动）恰一row、原顺序保留，binding2.receiptRunId与row.runId/attemptId全等；缺、额外、重排、重复或悬空映射拒绝。失败raw仍列同一完整runtime manifest。schema的header/terminal是外部原字节FileRef，不能把carrier.RawRange直接冒充FileRef；caller提取完整原片段并同时保whole raw和范围关系。

声明22、actual canonical23、frozen23、八runtime、四函数/checker/Python全域、observedPaths保false和实际部分列表、source/frozen null分域，全部按received CR-R/CR-H原义。headerPayload仍是原header/2完整严格解析值，绝不拼context业务字段或重写raw。未观察null/空列表不补expected；语法可解析但strict shape错误的header是malformed、payload=null。已观察错值/false不删除。

run投影不含全部typed/raw/stage业务信息，故row不能反建carrier；反向必须从同manifest解析binding2和完整carrier原件，核attempt/raw/不可变build票、全部child pieces与caller原件。保留完整carrier不是声称所有旧codec已兼容。M02–M05仍阻断真实旧metadata/helper/return adapter语义。

这里提出的是 **新的业务receipt identity policy**，需T03/root明确接收并提供精确 `receiptIdentityPolicyPin`。已接收v3四schema不变，未声称v3自动批准此业务对应；没有policy pin时可以保存captured原件，但不能宣称receipt-business兼容或启动。它修订的是R1自行要求“child runId直接等外部receipt runId”的关系，而非修改旧strict schema。若对方坚持将receipt.runId定义为child identity，则本路线不可采用，必须由原T03前向新版本明确identity union/null/required和双向迁移；本树不暗改四schema，也不以省掉失败attempt规避冲突。

## 3. caller witnesses 是独立来源集合

原 `Artifact` 完整定义保值不变，仍仅child stage/piece提取：非null stageId、pieceId、whole originRange必须能解析实际原child stage。caller 的exit/join/release/command/prior ticket不在child stdout内，不能伪造这些字段。

新 `carrier2.callerWitnesses` 为独立有序集合，CallerWitness明确origin=caller-owned-file、同attemptId、唯一witnessId、完整FileRef及原bytes/SHA、精确collectorOwnerPin/layoutPin、purpose/codec/fieldPointer和earlier parentWitnessIds。witness和child artifact namespace不得重名或混用。caller record不接受stageId/pieceId/originRange键。所有引用必须声明、同attempt、正确来源/角色、真实受控根、完整manifest成员且full bytes/hash一致；FileRef不是probe locator，probe不读取包外原件。

caller生命周期使用独立 CallerEvidenceValue，明确witnessIds；旧child EvidenceValue.artifactIds/sourceRanges不改，不能把外部FileRef偷偷塞Tree掩盖悬空引用。observed必须有同attempt且externally verified collector/layout/完整原件、可解析指针与值逐字相同，reason=null。已有bytes但collector/layout pin未知时用captured-unverified，保完整原件与实际值和精确reason，不能假称unavailable或observed。真正unavailable/not-applicable才value=null/空引用并给原因。未知actual pin仍null；字符串或文件存在不创造owner/handle/权限。

新显式codec `i05-caller-witness-payload/1` 是本规范提案，记录format/attemptId/purpose/value完整Tree，按已有C规范UTF8编码；witness.fieldPointer=/value。旧caller原件若是其他codec完整保bytes，需原codec/layout纯规范后才能解析，不能声称重编码与旧原件语义已证。collector接受记录与layout pin必须在使用前固定，不能自指未来自身文件。

purpose精确分command-context、target-binding、cancel-request、stopping、target-terminated、reader-joined、references-released、timing、prior-authorization、private-diagnostic。targetTerminated需实际owned target exit/signal原件及target-binding关系；request、stopping、child terminal不能代替。reader join、引用释放各独立保actual false/null/失败，不从exit推断。commandContext保精确argv/cwd/受控非敏感环境和原attempt登记来源。prior authorization保真实预先票全原件、owner/source绑定与先于dispatch的接受事实；序列化ticket字面不授运行权。

## 4. 无环、失败与未改项

依赖顺序：先前获批规范/codec/collector/owner记录及不可变build票→真实caller attempt登记/command与预先票→child完整双流和caller postrun原件→child pieces/caller FileRefs→carrier2→binding2→若到达才comparison→完整外部manifest→runtime receipt3。绑定不引用未来receipt；manifest不列自身和后出receipt，build票/provenance永久not-executed/null不回填。caller文件只RawSHA完整原字节；未新增自哈希字段或H域，原七H域/preimage、terminal prefix与metadata/source旧digest全部保留。

严格首错、全部已返回stage/typed/payload/rows/sidecar/source/definition/metadata/wire、false/null/partial、未到达状态、37期望/14held bytes/参数/golden、完整417与单B1差别、既有caps不变。private diagnostic不冒public四字段ErrorFrame；receipt错误actor/code/exit沿received CR-R真实保留，不把更早原失败改任意RESOURCE。新的容器不弥补旧codec/权限缺证。

新八份设计+来源/作者证据只在两既有business-carrier prefix追加R2命名成员；113旧件与AGENTS不改。有限检查只验证本次新增分支、caller文件/引用和31项投影，不重跑无关旧数学或RDF比较。合成pin/原件/receipt只用于设计反例，不能冒实际批准、运行票或完整JSON Schema引擎验证。待root原独审delta，不自认Pass或G02/G03真实接线闭合。
