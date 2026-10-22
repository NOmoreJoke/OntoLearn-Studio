# D2 business carrier 独立最小增量审查 R2

**结论：Pass，严格限于本次纯设计增量。R1-F01/P2、R1-F02/P2 在规范表达层关闭，未发现新增 P1/P2 表达矛盾。** 本结论不签运行、实际业务兼容或全程遵守冻结写面的合规结论。作者中途两次覆盖冻结旧件是实际过程违规；最终恢复和本次设计 Pass 均不抹去该事实。

## 固定范围与证据

- 工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design`，分支 `docs/I05-d2-consumer-design`。
- revisionBase `aefa82e51643e0a75ecb960645d63917b046edd6`；candidate `707c3915bc28a92955638cba4e6b8e3c18e8cfac`；process/HEAD `a23a2550c163e9571adebaf983f7c50909c2f09c`。
- 44 payload + manifest 为 candidate45件；后出 receipt 为 process第46件。独立核每件 current bytes/SHA 与固定 Git tree blob 一致，旧113件 current 与 revisionBase逐件一致。用标准 Git blob 前缀加原文件字节计算 blob SHA-1，对固定 `git ls-tree -r -z` 校验，未执行文件正文。
- manifest：10185 B，SHA-256 `cfc6a607290c4e0d14e5d3b71a5153be8fa81e65dd24616465b12f0ddfafc352`；author receipt：73240 B，SHA-256 `a20ec2ce67b89b425dabc24371ced0706afd48684b4a3bd00689defb2a447ef1`。
- 新14件完整 v3 与6件 feeR4纯资料分别逐源 repository/ref/path/blob/bytes/SHA核同。只采用限定设计接收的事实；没有读取 fee reference.py、产品/actual、其他WIP或 canonical-interface-inventory。
- AGENTS 15147 B、SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，与 R1当前规则一致；原外部 common/desktop/permissions 边界沿用。index空。

八份 R2规范完整读取/解析。文法只重审六个变化定义和七个新定义及完整关系；46个未变定义承接 R1。field map 全量逐值校验，receipt31项逐 received schema pointer/shape 校验，forward与missing材料只审实际增量。未重复运行旧 model、数学/RDF/产品回归或作者 checker。

## R1 逐项处置

### R1-F01/P2：设计层关闭

`wire-grammar-r2.json:3271` 起的 NotDispatchedCore、PreContextFailureCore、BoundContextCore 三分支，以及 `:3499` 的 AttemptCore，完整区分无dispatch、已dispatch但无受信context、已接受context。第二分支的 childRunId 是精确 null，完整双流 FileRef 非null，即使0字节；原退出/信号/首错均保留。第三分支继续以非空 child context身份约束 RunCoreBinding，没有将收到context后的失败清空身份。

`BusinessValidationBinding:2883` 改为 binding/2，显式 receiptRunId 与 attemptCore；Carrier 为 carrier/2。receipt.runId 的 required非空string和旧四schema不改。新 received责任索引 `/propertyIndex/755` 的 producer=caller，独立校验确为 caller；R2提出 receiptRunId=真实原caller attemptId，而 child runId 另经core关联。这个对应是**需T03/root接收的新业务身份policy**；Negotiation.receiptIdentityPolicyPin 当前实际仍null，收到完整 v3 不会自动批准本业务映射。无policy pin不签启动或receipt-business兼容。

独立从字段规范构造 pre-context exit7 的31键 receipt row、0字节双流和三个core形状，具体received schema关键词检查通过。31键逐一删除、null receipt.runId、额外childRunId均拒绝；自构反例还覆盖context前编child、存在context却清空/改ID、重复context、事后编receipt label。原R1无法合法表达的失败现在有明确规范路径，不需要省掉dispatch、制造child ID或nullable化旧receipt。

31项投影保存完整header FileRef与RawRange的不同类型、原headerPayload、false、partial/未观察值、source/frozen分域与首错；按真实caller registry保所有attempt原序，并通过同manifest中的完整binding/carrier回读，未声称receipt行可反建业务原件。外部真实registry/owner/source和实际decode仍是后继验收。

### R1-F02/P2：设计层关闭

原 child Artifact、stageId/pieceId/originRange 和child帧定义逐值不变。`wire-grammar-r2.json:3513` 的 CallerEvidenceValue、`:3571` 的 CallerWitness、`:3710` 的明确payload codec为caller-only原件提供独立有序集合；caller字段不容child stage/piece/range，lifecycle仅经witnessIds引用。完整attemptId、collector/layout pin、受控FileRef、原bytes/SHA、purpose/pointer、前序parent与manifest成员均有明确核对规则。

独立自造 reader-joined 原件，按C生成完整bytes/SHA/base64，实际Tree值为false；其CallerWitness和CallerEvidenceValue无需虚构child字段即可通过形状及来源关系。另构造悬空/child ID混用、伪stage字段、错attempt、request冒终止、未批pin升observed、缺manifest、原SHA错、未来parent、false改true等反例，逐一拒绝。observed与captured-unverified分开，未知collector/layout仍保存原件，不能冒observed。target exit、reader join、release、prior ticket各自实际来源不互相推导。

这些是明确版本化的**容器与guard设计**，不认证当前实际collector、旧codec、handle、issuer或资源许可。新payload不是把旧opaque原件重新签成兼容。

## 检查结果及实际覆盖

独立 stdlib检查实际 exit0，共17项检查、47个自构拒绝例。它们包括完整received schema具体约束的自编有限解释，不执行作者谓词、不用第三方JSONSchema引擎，也不宣称实现了完整JSON Schema规范。字段及来源证据详见 `independent-proof-r2.json`。

作者5份完整有限例分别是 zero-byte、bad-header、stderr-only pre-header、signal-before-context、not-dispatched。每份的Carrier/Binding和完整runtime receipt按本方有限grammar及received schema关键词检查通过，全部registry原件bytes/SHA一致。作者另有4条detached context关系前提。**没有完整post-context incomplete/collected业务端到端fixture**；本方只对这部分构造身份分支正反，不把它说成完整采集正例。此限制不阻断本轮R1失败可表达性修订的设计接收，完整采集/运行与真实source仍不能据此通过。

原stream2、严格18 header、四schema1241、原digest七域、child Artifact/帧及旧业务要求保持；本轮没有重跑或重签37期望、14held、参数/golden、417/B1或数学/RDF结果。M02–M05仍缺完整旧metadata layout/codec/recipe/live verifier/API return adapter；M06仅收到feeR4纯提案，不等于取得实际usage、issuer、capture、同issue17L、资源和source权限。

## 冻结写面事故与不能补造的过程证据

该事故不作“全程未改”表述。固定事件记录、原命令记录、check01/02 traceback及当前独立身份核对共同支持以下次序；事件没有独立wall-clock，不能补造时间戳：

| 原tool chunk        | 已保留事件                                                                                                                          |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| a0aaef              | 作者准备新checker时误写已冻结 `checker-source-r2.json`，初稿未单独保全。                                                            |
| e9f21e              | 在同一受保护路径再次修改源码，构成第二次覆盖；此执行态容器后另存新名。                                                              |
| e46f46              | check01读取覆盖态旧路径，子进程exit1，合成TreeNull缺value；完整原双流保留。                                                         |
| c8aaf9              | 修改新合成fixture；覆盖态checker仍占旧路径。                                                                                        |
| 233707              | check02仍读取覆盖态旧路径，子进程exit1，old113 hash门报 `old frozen bytes`。                                                        |
| 1fba4a              | 执行态新容器保全为 `business-checker-source-r2.json`，从revisionBase取回旧原件；restore `git show` 实际exit0、stderr空，113件再核。 |
| e1c36a及check04记录 | 恢复后从唯一新名运行check03/04，子进程exit0；后次仅修合成source前门错误码适用域。                                                   |

旧受保护文件现为12013 B、SHA `1d71c649c72ad2e59183be3d5f902b30944c5bab5d72e881d3e119dac6006fe4`，等于revisionBase Git。新执行态容器19751 B、SHA `e9ddf626425097d76a58c652a9829b6f1b0c4378588b3a65a54703ba8f2cb8ae`，与固定新candidate一致。这里的“两次写”发生于作者准备source容器时；本方静读新checker字符串，没有执行它，也未发现其正文另有输出文件写面，不把准备时覆盖误说成checker运行后自行改旧件。

check01/02/03/04真实子进程exit序列 `[1,1,0,0]` 和每次text/base64/bytes/SHA完整分流均独立核验。外层工具调用exit0不能覆盖内层exit1。初始两次静读错误c30796和57bfa2各exit1，但初始独立分流未保存，只能保留原转录引用，不能从后续读取重建。check01/02的编译诊断文件名不同不等于源码版本改变；原argv均保留，未改成后来新路径。

**精确缺口仍在：** 首次未执行初稿的完整bytes/SHA没有独立快照；两次覆盖的独立wall-clock未捕获；部分初始命令原分流仅有工具转录。现有证据不能重建这些不存在的材料，也不能用最终113相等证明中间从未违反冻结。`commands-r2.json` 对这些写入/恢复的若干外层操作只是chunk引用；本报告基于固定事件记录和可核执行态/错误流作有界审核，不声称亲眼重放了两次中间状态。

最终candidate完整性已独立核实，旧113已恢复；过程违规保持审计事实，不能因设计Pass解除责任或宣称全程合规。后继首次写入须exclusive create并对旧/候选成员预检查，本方新输出已如此处理，未碰作者路径、AGENTS、stage/commit或branch。

## 交付与停止边界

本方脚本仅指定Python3.12/stdib、PYTHONDONTWRITEBYTECODE=1，执行前静读imports与写面；正式命令保存完整argv/cwd/已知exit及lossless base64双流、bytes/SHA。仅本方新md/json使用指定Prettier与 `--ignore-path /dev/null`，具体检查范围和真实结果见本方format原件；历史作者证据/固定快照不格式化。

后出 `independent-r2-receipt.json` 固定本方精确成员、bytes/SHA，排除自身与其后capture执行记录以免循环；root另固定两者SHA。最终旧113/new46、HEAD/branch/index与仅AGENTS既有M加本方新件的状态由最终seal核验。封存后停止写入，root独有最终收件/采用决定。

本Pass只关闭R1两项**规范表达缺陷**。新business policy及stream2/carrier2/binding2的owner/root采用、实际pins/codec/source/权限、真实canonical首错、fee/issuer/allocation、Job/Store/whole-H、完整417/wholeOracleComplete=false、父137/S1/B1、平台/真人/指定双模型/CI/develop/远端门全部保留。
