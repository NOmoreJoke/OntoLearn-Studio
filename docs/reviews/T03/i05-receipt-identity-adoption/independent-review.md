# Receipt identity 最小纯设计采用：独立静态审查

结论：**MINIMAL_IDENTITY_DESIGN_PASS_ONLY**。固定候选 `3ddce89309c33e732e69f4ae668699ace6ffc13c` 对这项身份对应的限定采用表述可接收，未发现需修订的问题。可以另以 identity policy/1 明确 receipt3 的 caller attempt 身份及其 child context 关联，不必因此改变已接收四 schema、31 required 或版本。此结论仅属于本次纯设计窄审；它不是总控共同接收、实际 policy pin、stream2 全部业务兼容或实施/运行批准。

## 固定候选与实际读取

唯一树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-i05-semantic-offer-owner-review`，入口实际 HEAD 为3ddce893，base为 `d9c3c151614674f2c7a6e3d7f6507aa7ba81db58`，index空，tracked dirty仅已有保护AGENTS。AGENTS15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` 实核相符。

Git delta恰6件新增文件，全部在授权的 receipt-identity-adoption 两prefix：5payload53832B，加candidate-manifest1273B；manifest SHA256 `8255a54a9368833c693d9f4980c139141904f441d040844dbee9012475f59a25`。本轮完整读6件；全部payload current=固定Git=manifest bytes/SHA。没有修改d9c规范、四schema/字段表、旧报告、产品或其它树。

input-identities所列17件固定输入及3份控制原件均独立核 current=指定repository/ref/path Git=bytes/SHA。10件carrier R2固定在 `0841ffbe7a4599fbea96f4ff998808f3f4e00972`；七件已接收protocol3输入固定在d9c。完整读R2 spec/handoff、完整独审和root receipt，以及当前控制限定接收；R2 JSON只取本次身份、31投影、相关core/关系、原五例/四前提及缺件/采用边界核查。没有重开未改业务字段、旧checker或其余1241作整轮审查。

## 身份解释与版本边界

现有receipt3的 `#/properties/runs/items/properties/runId` 是required非空string，minLength1、maxLength8192；它没有在shape上要求等于child context身份，也没有在header/2新增该child业务字段。fieldIndex755的producer=caller只分配生产责任，不能据此推导业务身份已采纳。本候选明确承认需要新T03/root身份policy，未把原责任行或d9c设计接收当成自动批准，符合这个区别。

本次定义的receipt row.runId来自真实、先于child结果的caller attempt登记；carrier2.attemptId、binding2.attemptId/receiptRunId及attemptCore.attemptId显式同指该尝试。carrier2.runId及BoundContextCore.core.runId则只来自严格接受的child context。角色不被合并，尚无context时child为精确null，receipt row.runId仍保真实caller身份。R2 Id是既有ASCII非空pattern、max2048的子集，落入receipt字符串shape；不需要截断、改名、放宽null或新增31之外的键。

这一结论同时依赖本候选明确给出的必要条件：

- 每份receipt先固定一个完整、外部受信的逻辑registry/原序域，能由实际外部来源回到登记owner和原件。域内attempt唯一；不同域不能因同字面ID拼接，不能拆域漏掉失败，无法限定来源时只保capture并拒绝兼容结论。
- 真实新调度/重试有新登记和唯一attemptId，前次失败与顺序保留；同一attempt既有结果回读不造新attempt或新调度。身份不由PID、时间、expected、字符串形状或结果后补造。
- caller/child两角色偶然同字面并非错误，但各自来源必须独立真实；跨attempt同child字面不能去重、复用旧结果。大小写、原值和来源域保持，不trim或归一化。
- 缺少身份登记或mandatory外层buildReceipt、approvedBuildRecord、完整manifest时，不构造一个虚假的合法整份receipt。原件和诊断仍保存；run可表达not-started不取消顶层前置。

因此采用的是一项新且显式的业务关联政策，未改变旧schema的required/type/null/strict shape或CR-R/CR-H。后继若要求receipt.runId成为可空child身份、增加identity union/新键、改31约束或旧CR，则须前向新规范和迁移审查；本次Pass不覆盖。

## 三个失败分支与原件保全

NotDispatchedCore的childRunId固定null，原真实未dispatch事件才可产生not-started；receipt仍有登记attempt键。已dispatch但无context的PreContextFailureCore保完整stdout/stderr FileRef，包括0字节；它不能因没有输出变回未启动。只有原CR-R实际probe前置exit2等条件满足才pre-header-rejected，其余保持incomplete、真实exit/signal及首错。

严格接受首context后，BoundContextCore保该child身份和已有stage/false/partial。第二context、后继坏帧或失败仍触发拒绝/incomplete，保第一已接受事实及全部后续拒绝原件，不能以“唯一context”为由回滚成从未取得身份。坏行里的词法runId、合法header但缺context、terminal样字节都不能建立受信child身份。这与固定R2的ATTEMPT-IDENTITY/FAILURE/CONTEXT规则及三个core定义相符。

header/terminal的RawRange与receipt FileRef没有被混用：后者要求外部实际提取的完整原片段及bytes/SHA，能回到whole stdout、原range和同一manifest。所有已dispatch双流即使0字节也保持非null FileRef。receipt row自身是有损投影，反向不能凭31字段或ID重建typed/context/stage；必须读同manifest完整binding2/carrier/raw/caller原件和同一原build票。登记全序中每attempt恰一row/一binding，缺项、额外、重排、重复、悬空或错域均明确拒绝。

依赖方向仍为先前受信规范/原build票→真实登记/command/prior authorization→raw及caller后出原件→carrier→binding→若到达的comparison→外部manifest→receipt。没有未来receipt hash回链、manifest自列或build/provenance回填；本候选本身也未伪填未来自身policy ref/hash。

## 全31项窄核及其它30项限制

独立逐行核31个sourcePointer、field、schemaPointer、required、完整projection文字、owner和unavailable，均与固定R2 `receipt-projection-r2.json`原行相同；其31个receivedShape逐项与d9c receipt3对应子树相同，required原顺序和additionalProperties=false保持。比较为类型敏感递归：先核type相同，再核dict键全集、list顺序长度及叶值；False不等于0、True不等于1，不依赖Python宽松 `==` 冒充形状一致。field755与R2所引责任原行也核同。

只对runId角色/关联作新语义接收；其余30项仍完全受原CR-R/CR-H、来源与可用性关系约束。31行文字与shape核同不是实现、完整业务兼容或真实观察认证。尤其command mode/selector与实际header值分开保留，原错ref/digest/mode/selector或false/partial不能改成计划/批准值；不匹配保持incomplete，不由本身份政策重定义其它字段。observedPaths必须含实际已观察false/非null叶，不能改mask吞掉事实。

本候选没有将上述边界扩成stream2全体、费用、caller witness issuer/layout、collector、旧codec或真实受控根的采用。actualReceiptIdentityPolicyPin及七项currentRuntimePins全null，executionAuthorization=false；另需外部真实共同接收和各实现/运行窗口，不因本报告Pass自动生效。

## 反例、历史与未验限制

26条反例是完整文字hypothetical要求，每条executed=false；三条非拒绝边界也清楚保同attempt回读、角色同字面及跨attempt同child字面的合法含义。没有把这些文字写成已执行拒绝测试或生成完整post-context fixture。覆盖包括空/伪身份、错角色/登记域、漏失败/重排/重复/覆盖重试、context前造ID、后继错误抹事实、0字节当null、RawRange冒FileRef、全31删键/加键、假policy/外层票、改观察、循环引用及过程事故洗白，未发现本窄政策的缺口。

固定R2仍只有五份完整synthetic失败例和四条detached context关系前提，缺完整post-context incomplete/collected端到端fixture；本候选如实保留。原两次覆盖冻结checker、最终旧113恢复、未捕首未执行初稿bytes/SHA、独立事件时间和部分初始分流缺口，均以固定完整独审/root原件保存，没有宣称最终恢复等于全程合规。本独审只核这些固定记录对本次边界的约束，未重放事故或重新审计旧113全过程。

实际检查仅普通文件、只读Git、stdlib严格JSON/哈希与31项文档关系，首跑全部完成、无本轮首失败；检查表见independent-review-checks.json。没有执行作者或R2 checker、没有模拟新业务fixture、没有重计/运行其余1241，没有产品import/compile、collector/fee/runtime/caller/native/GUI/SDK WIP读取。没有占用T04桌面、安装、网络、模型任务、stage或commit。

后继仍须真实登记owner/source/order/重试、raw捕获和首context后失败保全、完整post-context正反原件、31项双向闭包、collector/layout/受控根/prior ticket及其它30项实际域核验。M02–M05、真实codec/issuer/usage/费用/17L、whole-H/SQLite损坏HOLD、417/B1/S1、两OS/真人/指定双审/CI/develop等原门未关闭。
