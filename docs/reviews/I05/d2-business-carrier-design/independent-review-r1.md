# D2 business carrier 独立审查 R1

**结论：Fail，严格限于纯设计。发现两项 P2：pre-context 的真实 dispatch 失败不能形成规范要求的 companion binding；caller 自有生命周期原件没有合法 provenance 分支。** 两项均影响本提案声称完整表达的失败与证据路径，应形成新候选后复审。未知旧 codec、完整 v3 尚未采用及运行未授权本身不列为缺陷，也不被本报告关闭。

## 固定对象与审查方法

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-d2-consumer-design`；分支 `docs/I05-d2-consumer-design`。
- base：`dc3fc7768167f206e09b410da4f737199d2c5e18`；candidate：`cedefb069ddf77e48c2764793490517ab967aae3`；process/HEAD：`3f171f7d1fb481d669acb92b835b4bb96a3bc584`。
- 31 payload、candidate 内 manifest 第32件、process 后出 receipt 第33件，独立逐件核 current=指定 Git=声明 bytes/SHA。旧 D2 的57件逐件等于 base，未改。index 为空。
- manifest：6998 B，SHA-256 `26bc6ee415bea5eeee766f8783beeff62c8d46f9bbe2160f2c8256ab5de002cc`；candidate receipt：96947 B，SHA-256 `4e63a80ca83890f5a328fc51538830e6bdc53897b1dd95e9fe02541c5e09e251`。
- 已完整读取当前 AGENTS（15147 B，`de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`）及外部 common、desktop policy、review permissions；本次指定的纯设计与写面限制优先，未扩大为产品、GUI、网络或安装授权。

七份设计文件完整读取/解析，文法按定义分块静读。对251字段映射的重复列作全量逐值等同比较并审读所有其余列的唯一值；对 D1 转录的9冲突/21 old-only 完整原行作深度等同比较，逐行保留新增列。五件 D1 快照分别与固定 `86d6297a8cac5ad780f1be4416ec9052b82f3aaf` Git 原件核同，两组限定 root closure/readback 也与外部原件核同；没有读取这些记录指向的产品函数体或实际锁。

独立脚本只用指定 Python 3.12 与 stdlib，执行前静读 imports/读写面；没有 import、exec、runpy 或运行作者 checker、旧 model、产品、测试或生成器。22项独立检查全通过，含两个设计缺口的稳定复现；这表示审查检查成功，不表示候选通过。独立 proof 中的9个跨结构 guard 是从规范构造的有限谓词与反例，不能替代 decoder、真实 handle、RDF 比较器或权限验证。

## R1-F01 / P2：dispatch 后尚无 child runId 的失败无法绑定

位置：`docs/iterations/I05/d2-business-carrier-design/wire-grammar.json:2757` 的 `RunCoreBinding`，特别是 `:2762` 的 `/definitions/RunCoreBinding/fields/runId/type`；同文件 `:2882` 的 `BusinessValidationBinding.runCore` 和 `:3235` 的 `BINDING`。相关说明为 `spec.md:9`（child 本次生成 runId、caller attemptId 只是调度标识）与 `spec.md:63`（真实 dispatch 后即使0字节也保双流）。作者坏 header 样例 `acceptance-rejects.json:751` 也在 dispatched 时保 `runId=null`。

最小情形：外部协商已批准，caller 真正 dispatch；child 在第一条合法 context 之前退出；stdout/stderr 均为0字节，header/context/terminal 均不存在，caller 只掌握 attemptId 和真实退出状态。该情形既不是 not-started，也不能观察到或重造 child runId。

独立 proof 的 `counterexamples[0]` 保存完整有限形状 Carrier、原双流 FileRef 和完整 Binding 尝试。Carrier 的 finite record shape 合法；将同一 raw 与 `runId=null` 放进必需的 `runCore` 后，仅得到 `/binding/runCore/runId: expected exact string`。这是从新 grammar 独立解析得到的静态结果，没有实际启动 child。合成 pin 只是“已在外部批准”的形状假设，不冒充真实批准。

`runCore` 虽有 nullable 外壳，`BINDING` 明确将 null 用于 not-started，要求 dispatched core 保完整 raw。把本情形也填 null 会丢掉此绑定并违反该关系；编一个非空 runId 则违反 child 实际来源以及 carrier/context/receipt 的同一身份要求。旧固定 receipt 的 `07-runtime-validation-receipt.schema.json:140` 还要求 `runs[].runId` 为非空 string，新设计又要求其与 context 相等，故不能靠暗改旧 strict schema 处理。

影响：正常失败证据无法按照拟定的 raw→carrier→binding→manifest→receipt 链接入，消费者只能拒绝本来必须保留的失败记录，或编造身份/省略关系；四种 availability 状态因而未完整贯通。

建议：显式定义 pre-context 的 child 身份可用性分支，保 attemptId、实际双流和退出事实；为 runCore 的 null runId 或单独 failure-core union 加精确 guard，并明确对应 receipt 身份规则及必要 forward delta。完整旧1241规范继续冻结。新增无 header/context 的 dispatched Carrier+Binding 正例，以及将 null 伪提升为 child 身份的拒绝例。

## R1-F02 / P2：caller-only 原件无法登记为 observed 生命周期证据

位置：`wire-grammar.json:1711` 的唯一 `Artifact` record，特别是 stageId、pieceId、originRange 的非 null 类型与其“actual owner stage / actual piece / whole source stage frame”含义；`RawRange:529` 仅允许 stdout/stderr；`EvidenceValue:572` 与 `relationshipRules.EVIDENCE:3215` 要求 observed 有实际 raw/artifact 来源。生命周期的 `targetTerminated/readerJoined/referencesReleased` 在 `:3140` 起明确归 caller/resource owner，不能由 probe terminal 自证（另见 `spec.md:67`）。

最小情形：child 没有任何 stage 输出便结束，caller 在其管道结束之后实际记录 owned-process exit、reader join、引用释放。该111 B合成原件及 SHA/base64、拟登记 Artifact 和类型拒绝结果都在 proof 的 `counterexamples[1]`。这个外部 caller 原件不在 child stdout/stderr，不存在可指向的 child stage、piece 或 stage-frame range。

按当前 Artifact 原样登记，三处拒绝分别为 `/callerWitness/stageId: expected exact string`、`/pieceId: expected exact string`、`/originRange: expected exact record`。填虚构 ID/range 虽可能满足简单形状，却违反 Artifact 的真实来源关系；在 observed EvidenceValue 内只填 value 而不附原 raw/artifact 违反 EVIDENCE；填 unavailable 又丢失本来已经取得的实际原件。把 FileRef 隐藏在任意 Tree.value 或将 artifactId 指到外部未声明集合，也没有补上当前有限文法规定的、可解析校核的来源分支。

影响：ProcessLifecycle 虽列出了 caller 字段，却无法登记它们在正常 caller 证据域内的原件；预先存在的 physical ticket/command context 与 postrun join/release 也有同类问题。这与明确区分 request/stopping/真实终止/reader join/释放的要求冲突，可能迫使后继实现伪造 child 观察或省略真实证据。

建议：保留现有 child-piece artifact 分支，另加明确的 caller-owned witness origin/file 分支（或独立 witness 集合）；用 attemptId、实际 collector/owner pin、受控 FileRef/完整摘要等关联，禁止伪造 child RawRange。所有 artifactIds 必须解析到精确声明集合。补 caller-only 失败原件与正常 join/release 正例，以及悬空引用、冒充 child-stage 和 request-as-terminated 反例。

## 其他覆盖与未决边界

- 52定义、39 exact records、251字段、全部 type refs、required/nullable/union/enum 与字段 map 逐值一致；全部规则引用可解析。15项旧 mandatory 行全部保原值并加具体容器落点，13族完整原格与固定原文逐行一致；未知 API return layout 仍被 M05 阻断，未签实际全字段兼容。两项发现属于跨结构表达能力，数量一致不能消除。
- 新 stream2 的 context/stage/observation/terminal 与外部 carrier 是显式新语法；旧 consumer2.1/profile3/header1 与新 consumer3/profile4/header2 双向拒绝，旧 strict18冻结。完整 v3 未物化独审采用，不以18键形状或五件 D1 方案当授权。
- metadata 原 bytes、codec/layout/recipe、同次 live verifier 与 display contentSource 分离；缺件只能 opaque/pending，字符串相等不签 observed-match。M02–M05 的未知没有从产品或 actual 补猜。
- artifact/BNode domain、同域共享双射、两端 schema/wire 及其余 exact 门明确；原 raw/metadata/source/rows 等 digest 不被 relationDigest 替换。七个 H preimage 向量独立重建一致；新增 false/null/重复/Unicode 向量验证域分离，terminal prefix 排除终态本行，无新增 receipt/self/future 循环。未运行 RDF/model 比较。
- full417/B1原 scope、cap、false/null/partial、先前成功stage和首错保全有明确规范约束；独立有限反例覆盖缺 prior rows、opaque 冒兼容、同 issue 字符串、跨图同 label、非单射与B1冒full。它们不构成417采集或真实首错证据。
- 26 lock/六 direct/23 canonical/22 source/8 runtime 与 semantic33/parent58/历史43+2writer45 分开；9冲突、21 old-only 的完整原行与 D1一致，未来实际pin继续null。公共四字段 ErrorFrame 与私有诊断域未混用。

G02/G03 的容器层仍须解决上述两项设计缺口。旧 codec 语义兼容、真实来源/handle/权限、费用/allocation/issuer/capture、F1/D1/R1/O1 真实首错、14 held、完整417/wholeOracleComplete=false、Job/Store/whole-H、父137/S1/B1、平台/真人/指定双模型/CI/develop/远端全部保持原门；本报告没有实现、运行或生产证据。

## 命令、历史失败与封存

正式检查由 `independent-r1-capture.py` 记录完整 child argv/cwd/已知 exit，stdout/stderr 都按原字节保存 base64、bytes、SHA。identity 的全部 git show 有独立命令流；provenance 另保存11次完整纯输入读回和9项来源核验。最初交互式静读保留于工具转录，provenance 明示后续读回是新调用，不重造先前双流。

identity、audit-01、audit-02、audit-03、provenance 均实际 exit0；audit 后两次为增加完整反例和精确原件摘要后的新检查，旧输出保留。作者 check01–04 的四个 exit1 与 check05 exit0 原字节/SHA全部核验；一次只读诊断 exit1 仅有原工具转录、未独立分流，该限制照原文保留，不由后续 exit0 覆盖。本方没有执行作者 checker，也没有改这些历史原件。

独立大 proof 为 `independent-proof-r1.json`；身份、来源、原命令流及脚本均为本方新件。新 md/json 仅使用指定本地 Prettier、显式 `--ignore-path /dev/null` 格式检查；结果原流见本方 format 证据。后出 `independent-r1-receipt.json` 列本次精确成员/bytes/SHA，显式排自身与其后出的最终命令流；两者最终 SHA 交 root 外部固定，避免自签循环。最终 git 状态与固定输入再核见后出收据及最终命令流。作者文档/固定输入/旧57/AGENTS/index/branch均未改；只留下 AGENTS 既有 M 与本方允许新件，root 独有最终封存权。
