# I05 语义打包草案 R2 独立 delta 复核

结论：**R1-01 closed，R1-02 closed；新文档候选有限静态 Pass。** 本次没有构建、source/frozen运行、实际loader/cache稳定性、许可证入包、source-package等价或外部oracle通过结论。原R1 Fail及其候选/清单完整保留。

## 固定输入与实际差异

唯一树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-build-offer-draft`，branch `docs/I05-semantic-build-offer-draft`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。R1 candidate `33972c5c495fcdd9af1c381c6b5d94d63117d08e`，R1过程 `3629486e50c49dc5767def2beaf872edb0080711`；本轮固定candidate及读取时HEAD为 `6ba273a892b18a5ebaedc07aea6f36584999adcf`。

已实际读取33972c5→6ba273a完整相关Git diff、`r1-resolution.md`、修订§4.3/4.3.1/4.4及受影响上下文、schema comment/descriptor actors、三个owner状态、collector/schema构造与static verifier的改动和新清单。只新增本报告/proof，不修改受审件、stage或commit。

独立核新manifest的41payload、1,388,730B，逐件current＝固定candidate Git＝manifest；清单自身另排。R1报告仍10450B／`50135a0c4dd1d4cf9f2d7935026442cdc392145683c1f0ffd914fe0f50df43d4`，proof仍10358B／`0b94c84e44024139e71cf312ae8f35d4dbae0eac5a6dbd2bca910c91e61ff2db`。首candidate-manifest、原validation-static、来源清单、整锁调查及suite清单均与R1固定Git逐字相同。AGENTS仍15852B／`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`受保护未暂存M；index空。

## R1-01：职责边界 · closed

主文§4.3将frozen consumer的批准措辞改为 `declaredCompositionRef` 语法与manifest声明关联检查；runtime模块检查明确是实际loader code对manifest声明的expected/archive指纹，而非probe自行提取archive或验证外部source。新§4.3.1给出字段级分工：

- T03生产真实Git/source compile、archive/TOC/函数索引、installed/RECORD/许可、日志/工具及后置provenance；root/外部接收方审owner接收、实际组合和外部见证。
- caller持有批准的固定外部证据前缀，launch前核receipt、外部来源/见证和当前完整目录，launch后核header digest/declared ref/runtime code与同一receipt回绑；缺批准或差异不启动/失败。
- probe只核严格结构/声明关联、固定bundle数据、实际Python与loader/函数/checker代码，header保 `externalReceiptStatus=external-unverified`，不代签approved。它不得解引用外部Git/source/owner/profile、日志、提取器、原installed/RECORD或包外receipt路径。

§4.4现明确是root/外部接收和caller完整来源义务，消除了R1所举“合法onedir包无Git/原环境/包外receipt却须由probe核全部批准”的反例。schema仅comment增加该分工，实际结构约束未改；descriptor同步新增 `verificationActors` 和 `probeMustNotDereference`，保原三exact argv、executionAuthorization=false与acceptedCompositionRef=null。没有新增通用路径、环境选择器或可信receipt载体，没有把声明变成批准。

新失败表把build输入/代码域/archive/许可缺件、caller预启动批准/来源/目录缺失、probe前置/loader拒绝及caller启动后回绑失败分开；not-started、前置exit2、未知异常exit1/incomplete及外部failed/incomplete各有明确归属，不能由进程exit0抵消。所有新增码都准确标为后继协议提议，不虚称2cf已有实现。

source第23自身pin也已分域：probe可观测本身实际source bytes→compile/loader code并发actualSourceSha/code，caller按批准composition第23pin核；不让probe嵌自己的SHA或未来composition commit，从而不引入自引用。frozen只核声明expected/archive对actual loader的一致性，最终批准关系始终在caller/root。

构建图仍为既有source refs→archive/code见证→后置普通provenance→包外全目录manifest→外部receipt→过程commit；职责修订没有增加反向hash依赖，也不使producer自报替代caller批准。动态checker仍为resources.CONTRACT原对象，无新alias/exec或公共资源修改。

## R1-02：source-only接收元数据 · closed

`static-collect.py`的第23owner literal与input-identities、guard-migration、profile-descriptor三份派生对象均统一为 `I05; root accepted source-only R2; runtime/lock/package not accepted; ownership retained`。这与既有source-only closure及主文一致，同时保留运行/锁/包未接收、原owner权属边界。

已独立对三个JSON解析后作精确差分：除该owner文字，以及descriptor的新增职责/禁解引用表外，全部结构和值与首candidate相同。2cf source ref、probe93848B/SHA、22供应模块、四资源、两资产、43旧guard与30同13异、全部writer refs/bytes、锁与417有序suite未改变。修订没有转移T03 writer或采用6891锁。

## 受影响上下文与有限解释

两份schema除build provenance的comment外完全同形；final receipt schema原字节不变。`sourceCompilation.source`仍区分Git与installed-distribution-source，Validator.run不会被强塞伪Gitref；实际archive/code/sourcehash各域仍独立，当前2cf frozen前置拒绝仍是现状。

`codeDomain.marshalReferenceStability=measured-same-domain`在本设计中只能覆盖T03实际source-compile与archive提取的同解释器域见证，不能预签actual runtime loader/cache稳定性。该有限解释由completion=`archive-code-source-bound`、runtimeParity=`not-run-by-builder`、主文对跨loader/cache未测的限定及新增caller启动后回绑共同约束。实施时仍须保存实际code-domain见证；真实loader/get_code/fresh-warm/cache验证是另授后继runtime门，缺证或不一致拒绝并作显式算法/候选delta，不拿builder字段补填通过。

静态verifier仅新增owner/actor断言与单独输出validation-r2路径，旧validation-static保持原字节；本agent未执行该脚本。生成器改动仅生成相同schema结构的责任comment和descriptor职责字段，不编译/导入业务。新清单和处置准确保R1，不倒改首Fail。

完整417/320、83/106/54/50上下文、C13、生产/恢复/DAG/roots/失败原件、T05新oracle未正式收件与allocation/date首码pending仍保留；不以历史78/4/1填expected。12 B1 fresh语义trial、原12 S1真实snapshot、parent package:dir、正式Job/Store/selected/H、SQLite损坏HOLD/whole-H、全57P0/C–G/PRD10–12/六迭代、指定同版双模型/CI/两OS/真人/develop远端门均未改变。

本轮未发现由该文档delta引入的新阻断。Pass只关闭两项静态设计/账本一致性问题；原T03仍未接收本草案、meter HOLD未解除，实际实施/执行/构建/物理票仍须原owner与root另窗。

## 本轮未执行

仅Git/文件/stdlib JSON/hash与必要静态差分；没有产品import、probe/tests/pytest、builder/spec/reader/helper、fixture模拟、业务compile/archive解码、旧binary/witness/SDK/toolpayload、安装/网络/DB/native/GUI/计量或T03票；未stage/commit/push/PR/merge。现有Prettier3.9.10仅格式本报告/proof，未格式旧候选/raw。此内部独审不替代指定双方外审。报告/proof写定后停止写入。
