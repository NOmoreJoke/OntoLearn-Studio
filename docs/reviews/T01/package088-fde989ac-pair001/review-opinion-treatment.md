# fde989ac / package088 指定 fresh 双审完整意见处置

本记录是开发会话在全文阅读 MiniMax 683 行及 ZCode 259 行后，对全部意见的逐项处置；独立只读核对另见同目录 INDEPENDENT-OPINION-AUDIT.md。它不改写两份原报告，不把静态判断当新运行证据，也不为消除意见而松动既有安全合同。

## 候选、原报告与结论边界

- 源码 S：/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions；Git authority G：/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/.git/worktrees/T01-project-transactions。
- 当前 HEAD fde989ac2cd2fc59dc396b7082307f09235019e1，base 5f910b52c69d86a1076b2032e5d3c63e715947f3，40 commits / 546 files。两 fresh 审查覆盖同一候选/包，没有因报告文案误差造新候选。
- MiniMax 新任务 mvs_fb1d724db162453eb12a638ca81653ad，M3.1-Flash / xhigh / 始终授权；原报告95365B/683行/SHA256 82d112e961392a161fcb57bfe857d8c531502cd135d286db15243e10052bc71f。
- ZCode 新任务 session_e68cf42d4c3412e865cd3ed8ddbddcf3，Start Plan / GLM-5.3 / 最高 slider2 / 完全访问 / workspace memory OFF；原报告50991B/259行/SHA256 8d333399fc032b0b82fd486ae0ff80ee24dc77db976b0783ad52510e46d21518。
- 双方均判当前内部演示 PASS，正式发布/平台 HOLD；本记录不代双方改结论。双方新意见未在另一方运行期间互传。二者都明确采用相同人工输入与1790B单位补充；原提示词逐字冻结，11255B原清单各恰一次EOF。
- MM报告终验仅写本方report；Z中途在2/8结束输出，后同一会话出现“继续任务”并续作完成，发送者未单独确认。T01尝试续作的一次CUA因用户改变app被拒，未发送重复续作；无额度失败或重置。原始回执在COMPLETED-REVIEW-RECEIPTS.json及ZCODE-EXTERNAL-CONTINUATION-OBSERVATION.json。
- 2026-10-24T06:35:47Z静态终验：S/N各1288叶逐条bytes/SHA相等且tracked路径闭集一致；唯一工作修改仍受保护AGENTS overlay15147B/de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4；index175620B/c2af8c61f1279b0ebf40a69fd5150022da6a31e77c25cabb202da872a91741b3、cached diff空。详POST-DUAL-REVIEW-SOURCE-FREEZE.json。

## 本轮必要动作与暂不实施事项

本轮完成意见登记、证据及报告事实校正，继续原 push→PR6→真实CI→squash develop→远端复核。没有据本轮意见修改产品、测试、配置或包；不重跑已通过且不受文档校正影响的验收。修复未来确需变更的实现时，应新身份并按实际影响验证，不能抹旧失败，也不泛化为任何一字改动均重跑全部历史验收。

M1/M2/M3、records容量、原ACK责任、UNKNOWN与当前内部演示限制均未修复。不能把本轮内部演示PASS推为完整MVP/无人值守/大规模/正式发布可用。0/17口径不变，当前fde仍未推送；旧CI三失败不被本地全检或双审抵销。

## 核心§4容量意见的具体裁定

1. **真实且采纳的机制**：service:637-660中原未消费delivery的原token继续存在；同operation的新回复注册新token，其ACK只删自己，不代原ACK，原payload/full槽仍付费。selection()/dispose()不能凭导航结束旧责任。
2. **不是本轮首次发现**：旧pair002 review-opinion-treatment.md第50行已明确登记“同operation重复ACK不能替原ACK、旧token/full槽责任保留”。本轮新增的是UI入口定位，不能把旧已留账责任改说未发现缺陷。
3. **ACK丢失≠业务回复未接收**：preload/index.ts:26-45的ACK失败被catch后仍return delivery.data.payload；workspace-controller.ts:930-940成功accept会清pending。所以“ACK丢失后pending必留、恢复按钮必可点”不成立。业务reply未被接受的额外条件须逐项证明。
4. **按钮链必要前提**：main已offer；同controller仍活着；invoke已reject/返回而非永远悬挂；原owner/session仍健康；原pending尚在。reload/crash通常丢该controller pending；不能将所有崩溃/重载/ACK超时都替代为同一可达顺序。
5. **数量不能外推**：未ACK的A同时计入engine/IPC各自16delivery上限；通常这些门更早PERMISSION_DENIED，未必先到service735 INVALID_STATE。第16个A后B恢复也可能已无额外delivery槽，不能声称UI必连续成功完成16次恢复点击。旧原ACK若仍满足身份与会话约束也可能迟到可处理，“旧token永不consume”是条件而非重复调用必然事实。
6. **建议部分不采纳**：receipt不可达、窗口销毁、delivery不在某集合或新B已ACK，不足证明旧aliases/原责任终止。不得据此退旧holding、FIFO、代ACK或无偿退款。专用容量错误/明确自救说明可作为未来改进，但当前不为迎合报告另造错误目录或回收协议。

## MM Top10（§8）逐项处置

| ID | 决定与范围 | 本轮动作/仍存限制 |
|---|---|---|
| M1 同operation重复回复/full槽 | 部分采纳条件机制；不采纳“ACK丢失必留pending/首次新发现/连续16次恢复”外推及无证释放建议。 | 本记录上述六条校正；保留M3完整义务，不改产品。 |
| M2 uncertain单向闩锁 | 采纳既有M1，影响对应主链owner；health/tasks/job/result等不等于全App永久失效。 | 未修；不能简单允许不确定写或按UUID复位，future resolution须真实证据。 |
| M3 跨session创建回执 | 采纳M2限定于创建/示例；新origin不等拒绝属现行合同。 | 未修；不把session降纯审计或用稳定请求摘要替代原dispatch物理证明；Job/marker不是全局不可读。 |
| M4 未ACK两个16槽 | 采纳独立容量和无自动清理事实。 | 不相加为8次，不以时间/导航/换session退责任；所谓有界回收须先证明责任结束。 |
| M5 签名/公证/安装器 | 采纳正式发布欠项。 | 当前内部无签名目录包范围已授权；正式分发仍HOLD。 |
| M6 用户备份/恢复 | 采纳入口与验收缺口；迁移备份存在不等恢复演练。 | FR002/203及损坏SQLite物理HOLD保留；不说库必定不可恢复。 |
| M7 records及prepare残留锁 | 均采纳，分产品运行期与开发构建域。 | 初始1+15继任到16，第17个新record拒绝；现有效client仍先复用。锁残留/第三方删锁lstat遮蔽异常留工程改进；不能按年龄自动删他人锁。 |
| M8 平台/D2 | 采纳。 | 实测mac27，目标mac15、Windows、两Linux条件skip、参考设备及D2未验，不冒通过。 |
| M9 redo/本体整表/当前页导出 | 采纳现状，收窄规格判断。 | FR804未要求独立redo/历史选择器；Undo-of-Undo是真服务端前向补偿，不是假撤销；不是通用历史撤销栈。整表与当前页CSV保范围。 |
| M10 工程卫生 | 部分采纳nonce/fixture/大文件/潜在UTF8维护风险；否定无证NaN和messageKey缺失呈现结论。 | explainError按messageKey选固定中文模板并先safeDisplayError；合法params严格数值。workspace“*”为锁定仓库内包非外部浮动；invalidation-v2.json当前1745B全ASCII，非现cp1252故障；1627/1531行未超2000。 |

## MM §9（编号11–42，共32项）完整处置

| ID | 处置与必要边界 |
|---|---|
| 11 两份16槽 | 采纳；重复M4，保各自责任、不相加、不退款。 |
| 12 records16 | 采纳；重复M7，第17个新record被拒，不是16次死亡即所有调用失效。 |
| 13 本体整表 | 采纳；重复M9，服务端分页/规模待后续，不冒性能验证。 |
| 14 两Turtle入口上限 | 部分误判；semantic_execution._term先semantic._text已有1MiB门。semantic_scopes缺局部显式门仅留观察，须结合上游来源/能力面；未证两处均绕过。 |
| 15 删除影响投影 | 采纳UX权威性风险；前端投影非引擎权威undo-impact，未证完整Diff/确认被替换或提交失真。 |
| 16 busy finally | 当前重叠写反例不采纳；action先拒busy，disconnect不清busy，未证旧finally前有新action将busy设真；保维护风险。 |
| 17 焦点/aria-disabled | 采纳a11y欠项；真实selectWorkspace仍核busy/uncertain，能聚焦不等于已证越权切换。 |
| 18 CSV护栏/字符串cap | 部分采纳边界；N3限制使公式开头难触发不等不安全，导出受验证当前页/page/shape限制，缺单独字符串cap不等无界。 |
| 19 历史下一页 | 采纳UX限制；固定快照/顺序校验仍在，未证错页混历史。 |
| 20 无AbortController | 采纳底层取消限制；围栏非物理取消，不能为取消已入线写而撤销责任；仅未出现API不足证明缺陷。 |
| 21 controllers Map | 采纳长期保留风险；包含未决意图/Job，不能无条件LRU/换项目删除；回收须证明责任结束。 |
| 22 read微任务丢弃 | 条件UX观察；序列/退役门为防陈旧，另有单飞/合并刷新，未证应发读永久丢失。 |
| 23 软硬删除 | 采纳语义说明；managed墓碑保来源，manual删除仍有历史，不等不能撤销。 |
| 24 seen65536 | 采纳有界session上限/防重放，未验规模，不外推。 |
| 25 内部异常事实值 | 内部含值属实，public分类固定码/受限params；未证泄露，按潜在留账。 |
| 26 再撤销冲突 | 采纳保护行为；保ABA/后继编辑冲突，不统一no-op。 |
| 27 createIntent内存 | 采纳限制；重启新operation同名是新请求，不能自动叫重复副作用；原operation跨session仍M2。 |
| 28 内部create_project | 潜在误用留账；当前协议不可达，未证已绕过正式创建。 |
| 29 workspace.py | 测试易失模型误用风险留账，正式draft另路；未证当前持久草稿丢失。 |
| 30 OntologyPage客户端Diff | 更正：组件有生产调用，但production传previewManagedEdit先走权威路径，旧previewEdit/本地展示支路未采用；不能说整个组件无生产caller。 |
| 31 测试profile保留 | 采纳卫生观察；失败profile为验收原件，不统一删除；后续明确保留/清理政策。 |
| 32 文档/归属 | 采纳正式化欠项；个人appId/仓库名不单独证明法律归属。 |
| 33 Python Dependabot | 采纳覆盖缺口；手工锁升级不等自动扫描，不自行升级依赖。 |
| 34 弱断言grep | 不采纳模式命中即弱测试；空集合/truthy可为真实负例或辅助断言，须逐case证明缺业务预期，现无新具体反例。 |
| 35 ACK测试覆盖腿 | 采纳在IPC业务回复层而非engine→main腿；领域engine持久化、main intent为内存，不能暗示缺已承诺main持久账本。 |
| 36 缺失profile模块 | 维护风险留账；正式query现用execute_request；非所有import都被except吞，有些try外。接线前修闭包，未证当前生产可达。 |
| 37 单飞拒并发 | 采纳设计事实，保有限拒绝，不改无界排队。 |
| 38 Undo重复扫描 | 采纳源码风险；实际规模/耗时归D2，未测不量化。 |
| 39 全局book跨项目 | 采纳共享book事实；按job.projectId找原pending、localstate另核项目，未证跨项目覆盖/扩权。 |
| 40 Git历史前置 | 采纳浅克隆文档欠项；CI全历史已修，固定旧reader测试不删。 |
| 41 非POSIX NOFOLLOW | 采纳降级/非合作写者竞态边界；无实际Windows逃逸证据。 |
| 42 uv工具前置 | 采纳新增依赖；“未先uv sync必失败”过强，uv run --frozen允许按锁准备环境，README本已列uv sync，可补钩子说明而非称干净环境已证失败。 |

## ZCode Top10（§6）逐项处置

| ID | 决定与后续 |
|---|---|
| Z1 远端CI三失败未闭环 | 采纳为原pipeline下一步硬门；本地绿/双审不等远端绿。ROOT全文接收后推同候选，观察真实三job，全绿前不合。 |
| Z2 M1/records16 | 采纳既有限制；按上文M2/M7精确范围和计数，不将全App不可用/health重启必增record混写。 |
| Z3 M3十六责任 | 采纳已有安全合同及两个真实来源；保义务/计费，ACK失败仍返payload和恢复按钮前提按上文纠正。 |
| Z4 注入下consume失败 | 采纳潜伏脆弱性；无自然触发证明，不把直接receiver重试叫产品恢复。未来原frame/session同delivery私有有界ACK重试须新设计；当前不为注入例扩scope。 |
| Z5 M2跨session创建 | 采纳限定范围；未来resolution须原dispatch物理绑定，不删origin、不扩持久intent账本。 |
| Z6 正式签名/身份 | 采纳正式硬门，内部目录包范围不豁免正式分发。 |
| Z7 wholeAPP法律/_distutils | 采纳；mechanicalClosureOnly不等legalFullClosureAccepted。 |
| Z8 备份/恢复/PRD缺口 | 采纳未完能力/验收；保持FR002/203/300、损坏库B/C HOLD，内部子链PASS不冒完整MVP。 |
| Z9 跨平台/规模 | 采纳mac27实测、目标mac15未验/Windows/老设备/D2等边界。 |
| Z10 UX/卫生/a11y | 部分采纳；a11y/i18n/组织与依赖覆盖未核保留；messageKey/NaN、1627超2000及悬挂import全部吞异常等沿用失准确按MM对应更正。 |

## 报告自身事实误差（原MD保留）

1. Z §1.3所谓prompt声明7298、actual7296的差异不存在。T01直接read_bytes对原timeline及三个原冻结文本核：timeline17590B/SHA256 49a2c19acd047f0ed7223e30dde80208b8b4c097037296c9f4b8a62f4264aada；shared-prefix/MMprompt/Zprompt逐字声明均同7296，错误7298片段出现0次。ZCODE-HASH-CLAIM-CORRECTION.json保存物理字节证据。判为Z声明值转录/解析错误，不改源/原证据或prompt，不重跑产品。
2. MM §6.2 APP910分项应545文件+351目录+14符号链接（root目录另列）；报告352目录将root多计1导致分项911。原ROOT库存910保持，不凭文案重打包。
3. MM §10.1“§9全部42项”实际为编号11–42共32行；本记录完整处理32行，不丢其意见。
4. Z §4.3“两个checkout是quality/mac，Windows未动”不准确：ci.yml第二checkout位于desktop matrix，同步作用Windows/macOS；fetch-depth0并非只作用mac。Windows cp1252修复由八处UTF8另行解决，两者均保。
5. “messageKey不直接原样显示”不等于没有中文解释；当前合法数值DTO经严格schema，缺参数或任意NaN对象不能当产品可达反例。1627/1531行未超过2000，只有所列2623/2589超过该阈值；文件复杂性仍可维护留账。
6. ROOT核第三次renderer时只读脚本曾误假定成功对象必含error字段而KeyError，已更正缺省读取；这是工具读取错误，不是新的产品失败。原第三次PASS及所有真实FAIL均保持。

## 清单适用性、额外未核及HOLD完整承接

两报告的清单分类、全部适用未核/未满足及13人员角色条目均承接留账，不把“当前不适用”当已有能力。账号/多租户/支付/邮件/云infra与无模型前的AI能力按当前本地单用户无服务端形态不扩建；一旦接入对应面即需重新审。无服务端不自动证明备份/恢复、数据删除、桌面安全/a11y/错误提示等无义务。两报告未直接读过的源码/运行面保持其未核口径，不把历史引用冒本轮逐字实读。MM一条explore lane两次只读历史提取成功；Z未使用子agent，均不替代实际产品运行验证。

具体持续保留：正式签名/公证/安装、wholeAPP legal/_distutils、Windows/Linux原条件skip/参考设备/目标mac15兼容、无开发环境设备启动、D2负载/索引计划、损坏SQLite物理保护HOLD、用户备份恢复、FR002/203/300未完、真实LLM/S3前密钥存储/提示注入与花费eval等前置、静态加密/失窃预案、渗透测试/安全问卷、谁查看审计、全屏/表单/后退/a11y/i18n/RTL、依赖advisory/Python自动扫描、远端分支保护、组织归属与bus factor、C4–C6/D8历史及指定双审积压；未解除也未新增豁免。

所有历史原件继续保留：086首产品FAIL、087 guard拒绝0productcase、三真实CI失败、fresh001环境失败、088首Electron供给准备失败0packageattempt、renderer真实FAIL/FAIL/PASS。native首次0来源UNKNOWN与renderer第二次人工输入的适用时刻严格分开，不称全自动或全程0retry。实际宿主macOS27.0.1/Darwin27.0.0 arm64；macOS15 arm64仍目标UNVERIFIED，旧“15实测”报告不改写。

## 当前可推进与未完成

本轮完整报告及意见处置已形成可供ROOT全文接收的结果。无产品/测试/包改动，故运行证据身份仍为fde/package088，不为报告事实勘误重构建/重审。当前仅具备推进原修复PR流程的内部审查结果；尚未push/新CI/merge/远端复核，0/17仍不变。下一步以ROOT对两原报告、终态来源及本完整意见记录的实际接收为界，按原授权推进，不以本文提前宣称合入或发布完成。
