# T02 本体编辑状态

2026-10-21（Asia/Shanghai）。Owner：本聊天 `01a15bcd-f40b-7c91-81fa-7c481d2030d5`。

- Worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology`；分支 `feature/weekly-t02-ontology`。
- 已实查 base/head：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；启动时仅 ` M AGENTS.md`，无其他争写。指南 SHA256 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，保持未暂存。
- 已建立本功能独立 Goal；全文读取启动/共同指令、controller-handoff、plan、T02任务、requirements/acceptance、decisions/review、原 FR-200–204/C–G/10–12 和仓库指南。指南引用的 m0 更新计划在本 base 不存在，以主 checkout 同名源补读；不复制产品内容。
- 唯一写入边界：启动提示列出的 ontology Python 包、`test_ontology_*.py`、renderer ontology 目录、`t02-*.test.ts`、ontology fixtures、本线 reviews/iterations。未改 root tasks/state 或共享文件。
- 当前推进：独立服务/页面 C2 已有恢复提交；C3 补真实批准 Store2 只读 RDF 来源绑定，正式接线/指定外审门仍待。最新证据见末段，原阶段记录保留。
- 正式接线缺口：T00 公共严格 schema/命名桥；T01 同库版本化预览/人类确认/commit/undo；批准 I05 Turtle 支持检查与无损往返；T08 草稿来源。私有模型只服务本线，非第二公共契约、Store 或网关。
- 所有 FR-200–204 及父功能跨模块验收保留。当前未正式集成、未双指定模型审查、未 push/PR/CI/merge、未上线。完整导入/往返及最终 Store 提交尚待联验。
- 仅无窗口 CLI/unit/Python/build；不运行本机 Electron/e2e/native/HMR、凭据提示、付费、密钥读取、对外消息或审查应用；指定外审资源由总控预约。

## 运行中操作政策回执

已在安全边界全文读取共同指令新增第九节和无桌面段，实际共同指令 SHA256 `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880`。保持原 Goal/分支/功能，不改写历史输入，不单因此重开产品审查；未发生额度告警、重置、付款、凭据读取、GUI 或对外发送。内审 agent `/root/t02_independent_review` 已实际收到并读回同政策。

远端只读核验：`git ls-remote origin refs/heads/develop` 仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。总控实际 `execution-state.json` 的指定外审队列当前为 T06-S1、随后 I05 C2；本线未取得预约，不自行操作审查应用。

## 本地实现与内审处置

已实现私有不可变 Entity/Fact/Snapshot、引用校验/完整删除影响、定义与断言分别预览、RDF 精确增删与元数据 before/after；独立 React 页面包含表格/类树/SVG 一跳图、定义/事实表单、多语言编辑与完整 Diff 呈现。无 Store 写入、能力注册或公共接线。

独立内审 `/root/t02_independent_review` 首审发现四项，已实施修复，等待固定 SHA 关闭复核：

1. 旧草稿被套到新 revision：绑定 draftBase/factBase，保留旧草稿并禁止预览，重新载入/新建才使用当前版本；实际 headless 覆盖 pending→新版本→旧回复、编辑后迟到回复、切项目卸载。
2. 单值名称/定义丢多语言：完整语言 tuples 与逐语言表单；未编辑语言原样进入 intent，服务 before/after 保留。
3. entity types 与 rdf:type facts 双入口分叉：内部投影唯一字段归属，facts 拒绝 type/label/comment；正式投影需 owner 保留 Store 来源，未私改公共格式。
4. label/comment 字面量绕过白名单：类型检查前置，负例通过；非字段入口仍明确拒绝。

自查另修复多行表单实时 trim 导致换行不能输入的问题，改为保留正在输入的空行、请求预览时规范化；headless 实际按键输入两条同义词且完整保留。引用影响额外保留完整 statement，避免不同语句按主体/field 合并。

T02 专属 Python 23 条、TS 3 条；headless 10 项呈现/异常核验通过。首次浏览器运行缺少锁定 Playwright browser 1248，保留失败原件；后明确选用本机既有 headless shell 1234，实测 browser 为 `151.0.7922.34`。不下载/启动原生窗口，不将该替代浏览器版本记为产品 Electron 兼容验收。UI 多行新增测试第一次预期仍为单行而失败，修正预期后同候选通过，原件均保留。

## 外审默认权限政策回执

已实际读取本树 AGENTS 新增权限段与 `external-review-permissions.md`，核对本树指南 SHA256 从启动 `db1fb184...` 变为 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，共同指令 SHA256 为 `df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4`。该追加由总控实施，本线不 stage 指南、不改配置、不重启 Goal 或计算。今后预约进入外审任务时须读回 ZCode yolo 与 MiniMax bypassPermissions 实际会话模式；只读审查、指定模型等级、同候选双审和无桌面约束均继续。

## 最新完整检查

`check-fourth.log` 已真实完成（exit 0）：633 vitest、1075 pytest、lint/format/typecheck/build/ruff 通过。此前首失败保留；本次之后仅更正 UI probe 的多行预期并追加流程证据，probe 实际重跑通过，最后 lint/format 再核验通过。`verify:sources` exit 0，核对12源。关键摘要/源与原件哈希见 `verification.json`；截图和原始日志留本地，未提交大幅原件。

## C2 新候选

C1 `438c6ade34795cb3b0111f0bca463d4fd091b393` 内审不通过原结论保留于 `independent-review-c1.md`；新增多行定义问题已修复，名称/定义均用 textarea，实际加载多行并按键编辑后全值保留。

已按总控通知核对 T09 固定 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的17 manifest输入及原PRD hash，只复制 manifest/G-base 原字节至本线 fixtures。新增3条测试核对完整原本体/断言集合、原 owl:Class 声明、多行元数据及行为引用阻止删除。不读取T09变化HEAD实现、不消费其服务或Store helper、不预填正式推导。原声明由私有 class_type/classType 保留，公共 adapter 尚待 owner。

C2 全仓 `check-c2-final.log` 实际 exit 0：633 TS、1078 Python；本线26 Python/3 TS；`ui-probe-c2-final.log` 11项 headless 呈现检查 exit 0，截图已查看，lint/format 后核验通过。首次 C2 测试将事实误按原数组顺序比较、UI 键盘快捷键未正确置尾的失败原件保留；修正测试预期/光标选择后通过，未冒充产品错误修复。详情/输入及原件 hash 见 `verification-c2.json`。

本地截图路径保存最新 C2 呈现，旧 C1 图片原路径已被新探针覆盖，旧哈希保留在 C1 提交中；原运行日志和固定代码/输入仍完整保留。截图不作为产品验收或不可变源资料。

下一步：固定新 SHA 完成独立关闭复核，交付总控精确服务/页面接口需求；T00/T01/批准I05/T08联验及指定双外审预约仍待。父功能未关闭，Goal 保持 active；未 push/PR/CI/merge/上线。

## C2 内审终态与恢复入口

独立 agent 已对固定 `5ef86a1da88d86f2de7b55a7e3be38b1e0f986b4` 实际返回**通过**，全部历史问题关闭、无新阻断。逐项证据及未验边界见 `independent-review-c2.md`。这是私有服务/页面的内审通过，不替代指定双外审。当前恢复以该实现 SHA 与 `verification-c2.json` 为准；`438c6ad`/`verification.json` 是旧C1历史。

具体可执行交接已整理在 `docs/iterations/T02/delivery.md`。本条与内审报告/交付文件仅追加流程证据，无产品/测试/配置/依赖/验收或基线变化；不触发无变化复测。待T00/T01/批准I05/T08具体接口及外审预约，Goal保持active，尚未push/PR/CI/merge/上线。工作树剩余受保护AGENTS未暂存，以及本地未入库截图；未修改总控状态或其他文件责任。

## C3 续跑进展

上一 Goal turn 分类为 progress：实际源/页面/样例/测试、C2内审和恢复提交已经完成。本次实查当前分支/head为 `feature/weekly-t02-ontology` / `ca7f25366cb9e11533004938b86d5b80a75fe4b4`，指南仍为78df；远端develop仍5f；总控最新记录中T01内部格式3/公共接线尚未批准给本线，外审资源仍预约T06后I05。本次没有把其他聊天意图/状态文件当成活跃进程等待证明，也未操作外审应用。

在独占路径新增 `source_projection.py` 和专属真实Store2测试；逐条核对不可变源与编辑器完整RDF，保留原fact ID/owner/source_row/managed_value、墓碑、多处支持、定义payload hash及显式引用边。复用批准Store记录校验，不创建Store实例或SQL writer；不生成提交计划/确认凭据，不推测metadata权限或definition→IRI引用。该新增使读取来源证明前进，仍不是正式T01写入或公共格式批准。

新13专项已实际通过（`source-projection-second.log`）；全仓check运行中，独立agent设计检查未发现实质阻断，最终固定C3 SHA关闭复核待完成。UI/依赖/共享实现未变化，不重复headless/包内/native探针。源/来源边界详见 `docs/iterations/T02/source-projection.md`。

C3全仓`source-projection-check-first.log`已实际exit0：633 TS/1091 Python，包含本线39 Python；新增13专项一次通过。既有C2实现/样例/探针源hash逐项复核未变，未重复无变化UI运行。原始日志保留本地，当前源码/批准owning source与日志hash见`verification-c3.json`；待固定提交独立内审终态。

## C3 内审终态

独立agent实际对固定 `49321221733ea927484647352e05e7d833cebc86` 返回**通过**；owning source、实现/日志hash匹配，原问题保持关闭，无新实质阻断。独立精确探针确认类型/名称原asserted身份、读取零输入改写及旧源拒绝。非阻断P3“交付入口仍指C2”已仅在delivery文档修正并读回；报告 `independent-review-c3.md` 保留原意见与处置。

当前恢复实现为4932122，最新流程记录提交另附其后；仅流程文档差异，不重复无变化运行。仍无T01/T00/批准I05正式接口授权与T02外审预约，完整父功能、双指定新审、push/PR/CI/merge/远端及上线未完成。Goal继续active。本turn有实际C3代码/13真实Store专项/完整验证/独立内审与可恢复提交进展，不是只重述状态或把总控文件当活跃进程等待。

## C3 后续路由核验与子阶段请求

上一Goal turn分类为progress（C3真实读取来源模块、13专项、完整check及固定内审/提交）。本turn实际重新核验head75694b1、指南78df、远端develop5f。总控执行记录的新事实是T01已接收Python4与canonical/main8、I06保留六壳文件；两个已生效协议全文及hash已核对，具体格式3实现仍未获准消费。此前交付/接口文档的旧owner路由现已修正。

已准备 `docs/iterations/T02/stage-registration-request.md`：请求按现有root子阶段制度登记精确T02-S1本地范围、全部有界验收与父功能缺口；root尚未登记T02或授予外审时段。请求保留完整FR200–204/导入/正式写入/模型/父发布以及同版双新审/CI正常合并门，不把私有服务或页面换成父功能完成。产品源码/测试/基线未变，未重复check/GUI。

通过官方wait_threads实际核验总控thread `01a154de-843b-7a00-8a80-51ba1c0aebce` 的turn `01a15bc8-732c-76f0-824b-dc2ae935c08b` 为inProgress，status active，revision52/cursor `a6fb72bc-870a-442e-8c5f-cb4caa4b7ecb:52`；再用该cursor等待真实进度变化。此为具体活跃聊天句柄的核验，不把文件/意图视为进程等待，也不意味着总控已批准本请求或依赖。

总控随后实际透传相同owner政策；已在安全边界全文读回最新共同指令，SHA `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`，第九节/无桌面/指定审查/逐任务权限规则继续，AGENTS仍78df。已归档输入保留原SHA，不重建Goal、不因纯责任政策更新重测产品。对子阶段请求的独立文档复核实际通过，无实质阻断；非阻断__main__路径歧义已改完整反引号路径。

40秒按revision52的总控wait被新政策输入中断（工具明确Wait interrupted by new input），没有当作总控终止或重启依据；随后对同一thread/cursor只读重取即时快照。未向其他聊天发送消息，正式共享/外审缺口仍不能由本地登记请求自行批准。

独立agent完成登记文档复核，通过且无实质阻断，P3路径歧义实际读回关闭，政策更新已由该agent全文读回。报告见`stage-registration-review.md`；本地请求仍待总控登记。官方同一总控thread/cursor即时复取返回revision53、turn仍inProgress/status active，最新真实commentary确认T01共享基础、T03/T04/T09独立服务登记，仍未有T02预约或批准。这是当前具体活跃句柄的verified wait；不把其协调进度等同正式接口/领域能力通过。

本轮仅责任/阶段请求/流程证据文档发生变化；实现仍4932122，原全Goal不缩减不关闭。未向别的聊天发送消息、未写root控制文件、未操作外审应用或改共享实现。最新共同指令仅政策生效同步，未因此重开产品审查或复测。

## 正式条件持续阻塞核验

本turn重查head `cab0d8e870d5a5b92a06a278ba05fd81b278b94b`、保护AGENTS未暂存和两张本地截图；产品/测试未变。root执行记录09:14仍批准develop5f、无T02-S1登记或时段，tasks中的T02仍保留旧启动head/owned_and_preparing，不能覆盖本线真实源。外审预约仍T06后I05，公共格式3/语义未批准供本线消费。

官方wait_threads实际读取root revision56的turn仍inProgress；T01 thread `01a15bba-0884-7401-b24f-f50c1fcf60aa` / turn `01a15bec-469a-7402-891b-434a3adaf4c9` revision19仍inProgress；I05 thread `01a15744-136d-7000-abad-46de101eadaf` / turn `01a15b51-8347-7b52-8265-6c56574e7275` revision423仍inProgress。两依赖owner分别报告内部修复/检查与包内验证，并非已批准消费。按这些真实cursor继续45秒有界wait，不把超时当终态，不重启任何工作。

阶段请求和候选已有可审阅实物；跨聊天message工具明确要求本人人类授权，不能单凭总控派发回报。已通过异步用户输入请求该发送授权，未获回答前不发送；待发正文已准备于 `docs/iterations/T02/controller-message-draft.md`，不表示实际收到。本线不修改root bookkeeping。

完整目标剩余的正式接口/语义批准与T02实际外审预约缺口已跨原C2、C3、路由登记及本turn持续存在。此前独立源/测试/内审工作已完成；当前继续接线必须改变外部批准/责任或获得具体接口，独占路径没有能替代这些门的合法写法。不能通过重复文档、替身、越权共享接线、抢占外审或无审push/PR制造完成。Goal未达成，保留完整目标与恢复源。

45秒官方wait返回：T01 revision23仍inProgress，实际新增回执为内部Store3验证完成、后续同连接claim/CAS仍继续且“正式业务3尚未启用”；I05 revision424仍inProgress，包内/原生验证继续。没有将这些活跃依赖终止、重启或认作已批准接口。发送授权问题仍待本人答复，未回答不视为同意；没有发送。

阻塞审计：同一正式接口/语义消费批准与T02外审排期条件自原C2结束、C3结束、路由登记及本turn四个连续Goal turn均未满足（此前独立工作虽有实质进展，也未解除该条件）。现在本线独立实现/必要测试/内审/可读交接已完成；下一必要步骤涉及未授予的共享接线/未批准实现/未预约审查，必须外部状态改变。新提出的消息发送授权不是三turn阈值的依据，只是待发回执的额外工具前置。全目标未完成，申请按持续阻塞门将Goal置blocked，目标/源码/原证据均保留；恢复条件是总控实际登记/预约及发布可消费固定接口/语义版本，或相应安全交接后继续。用户授权消息发送后可先投递已准备的具体回执，但发送本身仍不表示接口/外审通过。

## 本人授权后的消息投递

本人已明确答复“授权发送”。发送前实际核验流程HEAD `44e6e927fb0a073c1cdf1573a751a698a7579dae`、产品实现4932122及远端/批准develop5f；root09:19:52最新资源限定为无活动UI审查任务、T06在真实桌面/时段后优先，I05条件后续。已依本人授权调用一次正式send_message_to_thread投递候选/验证/登记与接口/外审预约请求，工具无错误返回目标root threadId。记录见`controller-message-receipt.json`，原草稿正文保留；没有GUI、密钥、付费或扩大外发。

root此前另已主动read_thread读取本线blocked终态，并指示后续直接读取本线现有status/checkpoint。此次投递依据本人新授权，不是把root消息当发送授权；后续不重复回传/创建候选材料。消息发送权限等待已解除，但正式接口/依赖消费与T02实际外审条件仍未放行，Goal保持原blocked，不重建/重测、不将投递当产品门通过。

## 总控实际登记回执

已收到root消息并实际读回 `service-stage-register.md` 的T02-S1新增登记（文件SHA `bfeaa73be3bfbfa4bdd80ae71d79e42e60acdadc96cfdbdc23eaea4dc33b2e17`）：拆分方向已接受，状态为“待独立范围与完整证据核验”，固定产品4932122、批准base5f，全部原父缺口及同候选指定双审/CI/合并门保留。root已确认读到本人授权发送的回执，后续直接文件/聊天读回，本线不再重复发送。尚无实际审计终态/外审桌面或正式接口批准，不把“将审计”记为正在等待的活跃审计进程。

本线当前流程head6c74124，实际核验4932122后apps/packages/tests/锁无差异，只有本线流程证据。原候选保持冻结，Goal仍为blocked；不因登记重建或恢复、不重做未变化验证，不操作GUI。实际依赖/资源变化后仍在原聊天按原Goal继续；若另做父功能未冻结工作，须先独立树/明确授权路径，不能混入冻结候选。


## 总控原始证据封存请求

已全文核验总控 `T02-controller-service-candidate-audit.md`，SHA `184fee056aac4a3ae685103f32046015cd48d9c2cce57aeb2c9263b554f1a67f`。按其限定保全现有证据，未改候选、验收或重跑产品/GUI/模型验证。

`evidence-archive/` 封存全部41份现存日志（含32份原索引日志和失败记录）、当前2张C2匹配截图及4份原始索引；47个原始文件加内嵌清单共48成员。压缩包548,417字节，SHA `43d9e20533885828a03c34392e8ae42ada23663c1cc338986c795c236f2a6b86`。逐项清单与实际新目录解包读回均已生成，原文件未修改；C1旧截图仍只有旧哈希且不可恢复，不重造。具体恢复信息见 `evidence-archive/README.md` 和 `archive-index.json`。

本次为总控要求的有界证据保全，原产品C3仍4932122，完整Goal保持blocked；正式接口/外审/CI/正常合并及远端门未因封存放行。仅本地Git受控保存，不声明远端或异机备份。

独立agent对封存内容只读复核通过（`evidence-archive/independent-review.md`）。已提交封存为 `c30927000bdf7fafd5f396c08b39ae3ce9829f6d`，随后实际从该Git提交读取压缩包及清单、恢复到新临时目录并逐项读取48成员，大小/哈希/原字节全部匹配；详见 `evidence-archive/git-readback.json`。核对4932122至封存提交的apps/packages/tests/锁无差异。未push或扩大授权，Goal仍blocked。

## worker 单文件维护交接通知读回

已在安全边界全文读取总控 `I05-T01-worker-ownership-handoff.md`（SHA `bdacff8a75adc3805b34e284e2d19c10750090e272439e8013f8a51fb7faf782`）及最新共同指令（SHA `ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff`），核验 execution-state 的交接为effective、接收/独立证据与协议相符。共同指令原b24完整字节作为前缀实际hash匹配；AGENTS仍78df未暂存。

`packages/engine/src/ontolearn_engine/worker.py` 未来唯一维护者现为T01，只从批准5f的9314字节/2fa848aa版本施工；不得采用I05未批准C3语义worker。I05固定C3继续冻结，需修先由root精确返还、T01停存；protocol/resources/语义/旧测试/build/CI及其他责任未随转，语义四路径futureoffer仍未生效。source wire/限额/公共3/ready/运行能力没有因此获批。

本线只记录责任路由变化；未改候选或共享文件、未重跑验证/操作GUI、未重复跨聊回执，原Goal保持blocked。

## 四文件基础层维护生效通知读回

已全文读取最新共同指令17891字节，SHA `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`；实际核验前16317字节SHA仍ff5f，完整旧指令前缀保留。已全文读取 `foundation-four-file-handoff-effective.json`，其状态为effective_future_maintenance_only、生效时间2026-10-21T11:40:05.102755+08:00。

T01现在唯一维护 `apps/desktop/src/main/jsonl.ts`、`apps/desktop/src/renderer/src/task-presentation.ts`、`apps/desktop/src/main/task-service.ts`、`apps/desktop/src/main/index.ts`，仅沿批准5f。I06保留 `apps/desktop/src/preload/index.ts` 与renderer的env.d.ts/App.tsx/style.css四路径及私有模块；其他责任不扩。原协议待门文本保留为历史，本生效登记控制当前责任；固定C4/e2c/961原字节只读，精确返还前须T01停写、保全SHA/WIP及root唯一owner登记。

此通知仅转维护责任，未授权startup/schema/新代码/runtime3/ready；原第九节、无桌面、指定双审及发布门不变。AGENTS仍78df未暂存。本线未改产品候选或共享文件、不复测/操作GUI、不重建或恢复原blocked Goal；未重复跨聊发送，供总控直接文件读回。

## 2026-10-22 指定双审已实际创建，完整积压保持

原T02 owner按总控短GUI窗口，通过CUA在两独立树实际新建并启动同版完整S1审查。ZCode `session_8fdff47bb96963af157c498504a58c72`／GLM-5.3／最高／完全访问；MiniMax `mvs_06002009bb614b3bb56905f07eb5b240`／M3.1-Flash／xhigh／始终授权。两树HEAD均ce1，产品493/base5f，当前AGENTS de15；58原delta逐项hash通过，原提示完整保留。实际正文、长附件/AX接收、设置/ID及运行证据见`round-1/launch-20261022/creation-receipt.json`和`foreground-release.md`。两任务尚未终态，不计Pass。原T06 session/stdio保持，前台已实际释放；原owner继续监控/读取完整报告和全部意见处置。

完整保留候选C1/C2/C3、证据恢复、范围登记、typed纯方案、准备/政策补充及未就绪父功能，逐行依据与缺口见`review-backlog-20261022.md`。历史C1/C2无指定Pass，不倒填；当前S1覆盖全部保留实现与历史闭环，纯方案未实施。后续供方采用/接口实施、父验收、全部指定新审/CI/正常合并/远端门仍待。原Goal仍blocked，未重建/关闭；本次实际GUI创建是外部状态变化后的已授权执行，不改原候选。

独立agent已对创建证据与完整积压台账返回通过，无P级问题，报告`round-1/launch-20261022/independent-creation-backlog-review.md`。这不是指定模型产品审查。只读实际请求另核两真实turn、max/xhigh及完整正文；MiniMax应用仅去掉末尾1换行，全部内容保持。文档格式检查通过；无产品改动，不重复产品验证。

## 2026-10-22 round-1完整终态及待处置意见

两个原任务已真实终态：ZCode model-io finishReason=stop，报告19506B/SHA af43f9ab…d0e4f；MiniMax assistant stop，报告36714B/SHA51e3b498…579f6。均在完整同版493上给有界S1 Pass，分别5项P3、P2-1及P3-1..5共6项，合计11项必须处置；MiniMax摘要误记4P3，原报告保留不改。完整报告、终态回复、原始验证证据分别11和27份已归档`round-1/received-20261022/{zcode,minimax}/`，receipt绑定真实ID/turn/终态及字节hash，两方58受审项终态无漂移。双方全check各独立633 TS/1091 Python，MiniMax另独立重跑11项合成callback UI并复现截图；不当父功能/平台/生产证据。

原T02已全文读取双方报告，MiniMax六项经独立agent静态triage，合并清单见`triage-initial.md`。root明确原493先冻结至两报告到齐；现已收齐，下一步在新独立树沿原T02独占ontology/专tests/harness最小修P2及采纳的P3、其余按事实记延期/部分接受，不改公共契约/共享路径/验收。所有改变须新candidate、必要完整验证、双方全新同版完整复审，不沿用原Pass；未push/PR/merge，父门与原Goal保留。

## 2026-10-22 C4失败保留与C5当前候选

当前修复源在独立树`.worktrees/T02-s1-review-fixes`、分支`feature/t02-s1-review-fixes`，固定产品`e5ad54e5762157cafe532c2a0c07c22e8dd737cb`，base5f。原T02先修类型守卫/补21项UI行为形成35aa，完整634TS/1133Py通过，但独立内审发现JSON未配对surrogate造成UnicodeEncodeError，C4原Fail与原始流完整保留于round-2，不改成通过。C5新增UTF-8文本守卫及31用例，无静默替换/归一化或改digest编码；完整check实际634TS/1164Py exit0，ontology112passed，独立C5内审通过，无新P级。UI六输入hash未变，沿C4的21项headless证据，不复跑/不当正式服务证据。

所有R1十一项意见逐项事实/修复/部分接受/延期见`round-2/disposition-c4.md`及`disposition-c5.md`；小写语言子集与正式前置parser仍有明确父门，原acceptance/公共共享/锁/CI未改。C5尚无指定新任务/新Pass，下一步完整同版双方全新审，不沿493双Pass或35aa内审。全量积压与历史候选保持，不关闭原Goal/父验收/发布门。
