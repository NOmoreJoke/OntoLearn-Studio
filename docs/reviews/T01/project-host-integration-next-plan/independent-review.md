# 项目宿主与 ChangeSet 下一方案独立审查

**结论：最终29575B/f7ee5b85方案无未解的实质计划阻断，可交总控作下一阶段有界决策。** 初稿一项P2（任意位置首次内容I/O权限gate）与一处cohort构造/发布顺序歧义已定点关闭。此结论仅支持方案，未授实现、启用生产3或采用I06未批准代码；真实位置能力/create幂等/unknown恢复载体等仍须在实施授权前冻结，不能以“方案可接受”假称这些实件存在。

## 本轮权限、固定身份与实际读取

本轮由主线转达根精确docs-only范围：只新增`docs/iterations/T01/project-host-integration-next-plan.md`及`docs/reviews/T01/project-host-integration-next-plan/`；本agent只写该目录`independent-review.md`。不改主计划、任何产品/测试、旧报告/冻结5de证据或总控状态，不运行产品、测试、探针、GUI/Electron/e2e/native/HMR或桌面审查应用，不重开已关闭ChangeSet内部阶段。

- 实际HEAD：`5de3fff8aa02c5d6e577938660e9362936d90550`；批准依赖仍`5f910b52c69d86a1076b2032e5d3c63e715947f3`，不把5de未合并内部候选当远端批准基线。
- 最初全文读取计划：27275B/SHA `c0b4ea4a8e83583b650f462abf96fede1e9cf0bcadd5f31ec75fd5b166816b72`；当时inputs为22项/8537B/SHA `8a4df7ff41c36f7369b552d618bc3175d2d8b54c081a7a8c726d6e4a7c724b67`。完整exec `f01bde` exit0。初稿身份保留，不把后续修订冒称首次输入。
- 最终方案：29575B/SHA `f7ee5b859e07f2fb37f101e089387cf6a1eb06a64073f60d43df4bfd0af6f64d`；最终inputs为24项/9628B/SHA `6163e733868f47b69ab4e758a834c5e31ced8e47eaf83e2c9ceb361887e409ce`。独立`c428ac` exit0逐条读24个固定Git blob并核bytes/SHA：14份5de现场等原字节、5份5f对照、5份I06合同与copies相等。只运行Git/hash标准库，不执行`capture-inputs.py`（它会写input副本和manifest，本审查不取得这些写权）。
- 中间输入：`b7fc65` exit0核24项时计划为28684B/SHA `6370a3ed424e3736144dbc3f0979433aba931fed7e1f894f495bae1290d3a142`；该值为作者处理本轮意见的中间稿，不作最终身份。`9d1257`实际读最终H2/后段差异，最终仅按f7ee…收口。
- 已读当前5de main/index全部、TaskService selectProject/view/原promise guard与恢复切点、Engine环境/构造scope和实际#send/request、Coordinator许可和正式分派、JobStore项目公开映射/目录前置、Store构造与现lease、应用CAS有关位置。未读取未批准I06产品实现。当前与预读命令`3ac9b5`/`90e36d`/`0dbc42`/`f1e2b2`均只读；部分合并输出被工具标截断时，不把未显示部分称全文读取。
- 当前660合同：`main-integration-handoff.md`与`format3-consumer-integration-request.md`全文读（`5c84f4` exit0），source lifecycle按本方案必要§2/4/5及固定引用条款定点读；其范围和hash详见inputs，不额外扩大到私有产品。

## 实际I06合同边界，不猜FS能力

精确位置与身份已实际回主线；以下是固定Git合同而非未批准实现依赖：

| 仓库 / ref                                                                        | 相对文件                                                   | bytes / SHA256                                                             | 对本方案有约束的内容                                                                                                                                                                       |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `.worktrees/I06-model-gateway` / `b1283bce1daf7198fc6b0b62f8b0a6bbffa5a874`       | `docs/iterations/I06/T01-owner-response-alignment-r1.md`   | 9168 / `64f16ecce5164cc9bc6272add415b121a15c201f25805dc8cb2593eae74cb6c1`  | §3.2真实metadata owner/受控I/O缺失；excludedRoots非动态registry；§3.4–5真实新UUID/receipt、最后await后再核，不把同ID select当导入隔离。                                                    |
| 同仓库 / `68dfd71a950bab0cda2e53776c4aa3c5e7819d5c`                               | `docs/iterations/I06/T03-source-lifecycle-alignment-r1.md` | 10487 / `af6bcc573caccbec86eb6b291b6bd9bd310bfd973053fd6f58824c8c75bdb00d` | 六项第6区分main未dispatch guard与已dispatch后Coordinator受理/撤销排序；read protection不是写Job授权，不以本地代次替跨进程顺序。该补充由本agent预读，未被作者列入本轮24输入，不伪称在其中。 |
| `.worktrees/I06-transfer-guard-core` / `961ce77f26accd11bd1cd3ad4a9e560cd3565e37` | `docs/iterations/I06/transfer-guard-core-v1.md`            | 11155 / `ad67e4e1837a6f630c3f5980f2add3e3bb8e9444a60071bb6c6e7e05e2b18879` | 仅metadata/token；contentIo恒rejected/unsupported，不解析consumer、不执行IO、不提供FS lease/handle/wrapper；check/revalidate无external atomic fence。                                      |

前两份实际全文`8ca5f0`、guard全文`dded2e`均exit0，`aee397`重新核原blobbytes/SHA但未重读产品。guard现purpose只export/import，且把DB根列为转移禁止对象；不能把此purpose直接复用为project-open/create，也不能“移除所有DB保护”后称新用途安全。模型初始化不可用不能当私有根为空。最终计划已显式落实这些限制。

660版本三份合同另有本轮真实角色：main integration保留模型独立失败/唯一owner；format3-consumer §3揭示sameUUID select早返和固定旧EngineSupervisor引用；source lifecycle要求旧未settled FS/picker继续计槽，以及source proof/Job确认/模型grant分别处理。最终计划没有把历史14/6路径文字覆盖最新维护交接，也没有借合同读取取得preload/renderer或私有网关写权。

## 本轮意见与最终关闭

### P2：首次内容I/O前缺强制位置能力/私有保护gate，已关闭

初稿H1原37–39行从native picker生成location记录后即可用库级许可枚举；H2原55行只声明metadata-eligible/hash不授DB权限，未把实际替代gate明确排在catalog/header读取前。具体反例是候选位置落入I06私有profile/凭据/audit或其active/retired物理别名：拿到用户picker结果、绝对路径或metadata-eligible并不能排除这个位置，尚未成为“项目格式错误”的探测本身已是内容读取。问题是**方案缺强制前置**，不是对5de未提供该入口的现成越权指控，也没有运行私有文件探针。

最终H2增加必需真实location owner签发、用途限定的可执行能力，完整inventory及active/retired别名/退役闭合性在首次I/O前核验；明确header/SQLite格式探测、catalog、Store、backup/migrate均在之后。unsupported/缺能力/incomplete/unknown/未证明平台固定拒绝，跨await及连接/发布前按真实fence复验，check后按path reopen不能自称闭合。961ce77明确不能满足。其新project-open/create用途另保留最小授权身份与同库单writer，不与既有禁止转移DB的规则混用；硬前置未到不以固定userData替代FR-002的可选位置。该P2在计划层关闭，**真实能力仍未交付/未测**。

### cohort构造与发布顺序，已澄清

初稿H2步骤4要求新child的真实hello，步骤5才“建立新Supervisor/TaskService”，存在把构造与发布混写的实现歧义。最终步骤4先私下构造candidate cohort、保持initializing且不发布当前项目，通过唯一实际child/lease做Store→Job→reconcile→hello；步骤5核项目与scope并完成固定engine消费者绑定后才发布。没有main第二writer，失败不把旧模型context复活。这是顺序澄清，不额外扩大架构或新API。

## 全方案可行性与范围核对

| 审查面                       | 实际依据和结论                                                                                                                                                                                                                                                                                                                                  |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H1位置模型与许可来源         | 一库多项目符合真实Store/公开映射，未擅改成一项目一文件。main fixture是当前唯一现成选择源；TaskService.selectProject不授engine权限。方案明确新增库级catalog/create gate与单项目scope分开，不让renderer UUID/任意无projectId方法获得库权限。身份/能力尚待根选择，不称已有产品入口。                                                               |
| 目录与真实公开UUID           | 当前public_project会在缺行时INSERT，故不可借它只读修目录。方案使用已有JOIN一致投影，缺映射/证据拒绝、冻结完整分页/同名项目身份，不补写映射。metadataVersion/域revision/operationSequence与draft generation分开，不把catalog行/hash当写授权。                                                                                                    |
| create幂等/原子性            | 当前create_project只把域/app genesis与public映射同txn，不等于正式幂等create receipt；全局claim引用项目，创建前身份尚不能假设可表达。方案正确要求完整请求/claim/receipt与最小DDL/namespace另冻结、跨请求同ID拒绝、丢响应回原事实，不借metadata.save假扮create或建第二可变账本。                                                                  |
| open-existing/create/migrate | 现Store构造可能connect新库并迁移、serve会mkdir，不能直接在新picker上复用。方案明确先选择host intent，open-existing零创建/迁移/降级、create独占不覆盖、显式迁移有准确备份与取消。alias仲裁覆盖DB/WAL/SHM/backup/lock，不把现字符串suffix锁或isAbsolute当物理授权；未知平台保留拒绝与实际验证门。                                                 |
| H2/I06生命周期               | 主动项目替换/同UUID重开与普通renderer刷新/瞬断分开。必须关闭旧GatewayApplication/context/grant/material、取消pending、排空自有writer/worker，并重建所有固定engine引用者；TaskService独自重建不够。实际未settled FS/picker不因abort/rebuild减槽，模型取消不承诺过去零发送。新组只在两层ready+project/scope/I06绑定后发布，local且不恢复旧grant。 |
| H3真实来源/具名桥            | draftTicket须来自实际批准编辑器/T08内容代次，人工/Agent来源分别归因，不用测试计划冒充producer。main注入真实project/base/host，renderer不能提交actor/write/session/confirmation/hash自由jobInput；有限桥继续可信sender/mainFrame/document和唯一canonical，不开放generic RPC。尚未把UI/producer接线说成5de已有。                                  |
| 完整Diff/一次人类确认        | 真实main获取全部引擎段并用5de helper重组，缓存/IPC独立计预算，不把16MiB域文档预算当Electron帧/RSS承诺。完整旧值可读，UI分页不截断；冲突/impactCompletefalse不能accept。只有实际可信UI的明确接受是人类确认，cursor/页数不证明人类看过，也不强加第二个确认。                                                                                      |
| main dispatch guard          | 当前request await ensure后#send直接写stdin，仅transport session当前性，view generation不能补这窗口。方案在真实write前同步核捕获scope/票据、来源CAS/代次与Supervisor/Session，覆盖confirm/create；未dispatch拒绝可说未发送，已dispatch另进unknown，未把stdin已读当取消已线性化。                                                                 |
| unknown与跨重开              | operation.get=null只有无marker，queued claim可能已在。方案可先完整job.list寻找，DTO/列表不足保持unknown并申请精确resolution；主进程崩溃时原request来源必须选持久intent或足够的既有claim只读投影，不能只remembered/内存ticket。已claim只恢复原Job/receipt，不自动重放/换op/签新确认。选择尚未冻结，不应直接授权实现该未选分支。                  |
| 旧合同与写权                 | 5de默认2，业务3仅explicit内部；新host启用生产3须根单独冻结激活/ready/回退。candidate路径而非写权，I06其余路径/私有服务与新测试先逐条登记，旧tests/构建/资源等不顺带取得。DTO合并不能整份覆盖未批准I06契约或逼T01复制网关实现。                                                                                                                  |

## 有限的实施前决定，不把设计往返变成目标

本方案是**下一阶段决策方案**，不是可直接按全部候选路径开工的implementation authorization。根要作的有限选择已经集中在§7；建议授权时直接写定以下交付/退出条件，而非再启动无变化普通多轮：

1. **位置/能力合同**：选真实库文件形态、project-open/create purpose、可信location capability owner及支持平台；明确DB/WAL/SHM/backup/lock与私有root仲裁。能力不齐时只可并行不依赖其IO的纯目录投影/原子服务准备，任意路径实接不计完成。
2. **库级host与项目scope**：冻结谁给catalog/create权限、UUID解析后如何安装/撤销单项目scope和失败返回；有限DTO/页预算/受信激活profile定稿。
3. **创建原子身份**：冻结create前后的library/project/operation身份、唯一claim/receipt namespace及必要最小DDL；只审实际增量与真实失败/退出证据，不新增第二writer/账本。
4. **cohort消费hook**：I06给固定持有engine清单、实际关闭/initialize边界与未settled状态；候选私建、ready后发布和失败处置具体到调用点。
5. **unknown恢复单选**：优先选择能精确投影原claim/context的有界resolution，或明确定义唯一持久host intent；不要把两个未选建议同时塞实现，也不要把完整job.list的可用性当保证。相关读取有当前项目许可，恢复对账不恢复自动写权。
6. **路径/新测试/证据**：按上述选项删减候选路径并逐条owner授权；只新增必要测试，保完整失败/原子/真实CLI+包、隔离实际IPC/native/人类验收。契约与实现变更才触发相应验证，不因本文反复测5de。

这些是明确已承认的开工门，不是本报告新增的六个未解决P2；文档可以在当前结论下交根决定。若根只批准H1/H2有限服务阶段，终点应是该精确合同/原子实现及其实际证据，不假称FR已完成；H3与T09/编辑器等可并行准备，各自真实交付后接合，不能无限等待所有未来功能才启动任何独立工作。

## 四入口与父FR范围没有缩减

已按PRD FR-001/002/003/004/005及FR-804原文与44地图核对应边界：四入口全部保留且无API前置；空白/打开先做不把另两入口删除，T09必须给至少一个完整离线示例与全部原模块/固定输入输出/失败/学习闭环。项目名/位置/模板、复制/重命名/归档/导出、删除明确确认仍由原FR/T10接通，目录不冒充项目包。

四类快照触发、全项目restore独立确认/覆盖清单、完整学习/audit/metadata/draft恢复、两P0模式同一数据格式、原FR-006完整消费者以及Agent A-01/A-02均未被本typed阶段替代。main/renderer真实展示与实际人类点击、目标OS/native/IPC、Q5、指定GLM-5.3最高及M3.1-Flash/xhigh同候选新审、CI/正常合并/远端仍是实际门。本文无功能完成度登记，也不改变原Goal。

## 工具与收口

所有本轮工具是只读Git/源文档/原字节hash与本报告写入/明确绕过ignore的格式检查；完整exec结果已emit，未运行产品、fixture、单元测试、包或GUI。没有为纯文档修改重复1125TS/2789Py或旧材料矩阵。作者capture脚本不由本审查执行。唯一新写为本报告；完成显式`prettier --ignore-path /dev/null --write`再同选项`--check`后报告最终bytes/SHA，停止写，等待根决策，不将其视为实施授权。
