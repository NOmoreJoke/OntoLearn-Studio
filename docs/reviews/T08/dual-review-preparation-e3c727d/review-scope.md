# T08 下一轮完整同候选独立对抗审查

这是材料准备，不是已创建任务。新受审候选固定为 `e3c727dd90e22e7add5f0db94cefb57901af61f0`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；完整新运行／历史证据固定于过程提交 `0932268ddaaac29511bd57d26737ad48de1e8495`。原开发树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-agent-model`、branch `feature/weekly-t08-agent-model` 只是来源，**不是新独立审查树或已获执行票的证明**。新 review cwd、detached/process HEAD、task/session/turn、设置读回与报告输出根均待总控实际登记，不用旧93516审查树或任务冒充。

本文所有包内相对路径均相对 `docs/reviews/T08/dual-review-preparation-e3c727d/`；未来须从实际独立review tree下的该目录解析，不把它们当workspace根目录路径，也不读取原开发树的移动文件。角色报告路径则相对未来实际独立review tree根目录。

## 完整原范围与结论门

必须实质审查当前完整累计实现和全部原验收，不能只审修复差分、六组DOM、摘要或有限S1。全文读取原PRD V0.6，逐项覆盖FR-800–806、900–902、904，FR-204/302/400协作，附录C–G及F、G.5 A系列相关边界，第10–12节全文，尤其11.3全部九类、12.2全部七项及Q9真实服务。FR-903保持原P1；原57项P0、附录/需求/验收基线及原延期安排不改。清单与数量不等于产品验收，集成前置也不是完整验收条件。

整体关键验收缺失时结论须为“不通过”或“无法完成验证”；允许具体说明已实现代码中未发现哪些问题，不得把局部Pass当父功能Pass。缺前置不能成为不读源码、不完成可做审查的理由，也不能以合成端口、SSR、协议手工消息或静态清单代替真实运行。完整审查是本轮任务，不是预设必须通过。

## 精确输入与阅读顺序

1. 核 `input-manifest.json`、完整产品树与base→candidate全部差异清单，核全部28源／测试／fixture；以固定Git对象为准，不读取移动HEAD或别线未批准实现来补空。`inputs/current-product/`是本轮源，源码统一`.snapshot`数据后缀，字节不变；禁止执行或编译这些归档副本。`inputs/current-context/`含本轮完整PRD、M0计划、ADR、锁、真实App/main/preload/contracts上下文，M0实际归档路径是 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`。
2. 原101项输入成员全部原字节保留于 `inputs/history-original/`，包括原完整审查正文、需求/验收表、controller计划/决策、旧25源、完整PRD、内审1–8、首次失败gzip/元数据、固定输入/CSV观测、717项原check等。旧93516身份、旧25/44/828和旧运行只用于历史，不是本轮28源或新运行；不得漏读旧失败、压缩原件及其限制。原679/691/706仅有摘要/成功日志SHA，不虚称其完整成功日志已补齐。
3. 完整读两份历史指定NotPass：`inputs/evidence/docs/reviews/T08/independent-review-roots-20261022/zcode-terminal-20261023/zcode-glm53.report.md` 与对应 `minimax-terminal-20261023/minimax-m31flash.report.md`。它们是**上一轮共同历史输入**，不是本轮对方意见。原M的1P1/7P2/3P3、Z的3P3及双方整体NotPass均保留。历史Z未逐字段展开三gzip/两中间JSON、M的Ruff计数差异/管道npm真实exit未知/首探针失败后改断言等限定与原件一并核，不静默升级覆盖。
4. 完整读 `inputs/evidence/docs/reviews/T08/post-designated-review-20261023/` 的14项裁定/争议、bounded observations、独审分析、修复独审1 NotPass与2局部Pass、737/739历史check及各原始日志。owner的采纳/争议和局部通过不关闭指定问题，由你独立判断各原意见在当前固定源是否成立。
5. 完整读 `inputs/evidence/docs/reviews/T08/dispatch-boundary-20261023/` 的微任务/上下文修复、修前3失败、112纯TS及其限定、独审、7a33完整752/1052、真实验收计划；再读 `mounted-harness-preparation-20261023/` 的计划与实现首轮NotPass/纠正复核、mounted01失败、02成功但覆盖被指出不足、03最终六组真实DOM、symlink拒绝负例、最终e3完整check及各metadata/result/raw、Electron自动下载触发命令/文件SHA/来源说明、28源与9依赖前后身份和完整交接索引。
6. 按完整树及全部base差异追查调用链和遗漏；不能只读28文件或旧44差异。原设计/所有历史发现、原始失败与后继修复都进入判定。规则以 `inputs/current-policy/` 全文为准，历史launch旧GUI限制按时点解释，当前实际执行仍服从本轮精确资源票。

## 必须实质检查的当前累计代码

- codec对未知/截断/空/非法结构、单choice/非流式/JSON、thinking响应与历史、多轮tool ID/关联/重放/长度是否严格；enabled响应字段与无tools历史规则分开，不默默降模式。受测provider pin由宿主预先提供，响应model/fingerprint在工具前精确复验；请求别名不硬等返回版本，不TOFU/模糊后缀，不把字符串相等当真实权重、effort、能力或质量证明。
- 整批参数先验、全部TrustedContext字段（project/revision/snapshot/scope/module/mode/有序选择）、执行微任务紧邻端口前及回收／答案时的复验，authority异常净化、取消/超时/迟到、并发BUSY与预算/重复ID分类；模型不能注入项目/授权/确认，跨问题不能清空全会话ID/预算。只读、草稿、隔离运行边界及正式ChangeSet独立确认仍完整保留。
- P1的JSON参数形状检查不是SPARQL执行门。default无ports也不是已验证真实parsergate；必须由获批I05/T04唯一执行器及T00 composition保证SELECT/ASK范围、禁外联/写入与安全拒绝说明。不得造弱lexer/关键词黑名单，BASE不自动等于网络，CONSTRUCT不笼统叫写入但仍按原P0支持面判断。具体接口未交付的缺口必须留在完整结论。
- 请求输出ceiling与响应自报completion超限检查不同于输入/total usage或费用控制；缺usage仍未知，不是零。事后拒绝不能撤回费用，不改变Q5或默认费用政策。I06仍须最终发送前检查真实总量/预算/主体/当前配置和隐私。
- 收据完整呈现，失败/取消/过期/历史不能被自由文本或仅引用成功项隐藏；provider失败、预算尽、部分批取消仍保留已完成草稿和取消收据，快照不可反写；异常code/getter/proxy变异不能将原始异常/路径/单元格/凭据送入本地收据或provider投影。安全枚举外发仍须I06授权。
- 实际messages/tools/reasoning/摘要/历史/错误、字段来源、当前隐私/策略/端点/主体/配置版本及完全本地切换的最终字节授权、凭据与日志权威都在I06；T08投影只是最小化，不能从模型body、旧prop或构造快照授予外发，也不建立第二设置/公共注册表/Store writer。
- 真实AgentSidebar源码与事件：七模块/两模式、最多四动作、本地/模型未就绪/缺handler/旧context的发送、retry、Diff、取消；同context同步防重入，全部context轴隔离输入/锁/错误，迟到回调不污染新context或覆盖后续编辑；React文本节点不能变成HTML或资源加载。DOM六组必须核实际断言、非busy正反对照、原错误oracle与后续纠正，而非只看pass摘要。
- 两份新fixture只能证明真实ReactDOM与Node纯会话编排。Node原生Buffer留在Node SSR bundle；专用测试binding不进入公共App。Chrome显式exe/hash/实际版本、锁/9依赖前后hash、真实output归属、全新profile/offline/页面request abort与失败留档须真实。合成端口AbortSignal/late result不等于T00/I04持久job取消/ACK/终态，组件截图不等于全App/native视觉或两OS验收。
- 原v1合成case、v2真实RDFLib/CSV输入及完整oracle不可删：Q01/Q02阶段、同数量错义A02、001/002身份/名称/行号、SPARQL原文/哈希、错误/取消/旧快照等都逐项核。手工模型协议和有限库probe不是实际NL生成、正式query/reasoning/behavior/scenario能力或Q9/11.3评估。

## 已有证据与剩余真实缺口

e3自身完整check owner实报752TS/1052Python、exit0；mounted03六组包含14模块模式组合与七轴，28源/2输入/9依赖前后同、Chrome155.0.8059.85、页面requests/pageErrors空。方案、实现、DOM和完整check的Codex独立核验只作为历史证据，不是你的运行或指定Pass；总控接收也不是替你批准。mounted01真exit1、02虽exit0但覆盖被指出不足，原件均保留，不覆盖成最终成功。

总控有限收件原文在 `inputs/controller-intake/T08-e3-mounted-actual-controller-intake-20261023.md`，5032字节、SHA256 `9d363775591a262350b333c71ea1b99286d7d930a270f41131a69bf7789ee0d8`。该收件未重审原26算法、未关闭原NotPass/P1/P2；历史Node二进制SHA未记录，保持UNKNOWN，不拿当前文件反推历史。总控仅核三PNG哈希，未做视觉审查；owner曾查看隔离组件截图也不是全App验收。最新T01具体后端执行票已发、实现仍在进行，尚无固定可供T08消费的获批供方，不把授权、开工或未来方案记成真实接线通过。

尚无T08实际获批I05/T04 parsergate与composition、T04 QueryPage同页、T00/I04真实job取消/ACK/终态、I06实际当前隐私/最终授权/安全存储/provider/费用、T01真实Diff/真人confirm/原子/undo/restore、T09实际离线/学习记录、原11.3/12.2/平台/真人/CI/远端和发布证明。不得复制未批供方、造第二组件/执行器或要求花费API来填空。具体依赖未交付不等于要等整模块完工，也不关闭相应原P1/P2。

## 只读职责、执行票与报告

当前只准备材料：没有新任务、新review root、GUI/浏览器/Electron、测试或setup授权。总控未来派发须先登记两棵独立实际树与证据/输入提交，读回每任务模型/effort/权限，明确各自可执行原check/headless probe、环境和互斥资源。不能从本文件自行启动或沿用旧任务/旧运行票。实际派发后的普通必要验证不能因历史“无GUI/CLI前置”被泛禁，但不得擅自扩SQLite HOLD/native/固定端口/付费范围。

只读实现/测试/依赖/配置，不改或格式化源、不提交/切分支/push/merge，不改冻结prompt/manifest，不读取secret/.env/keychain或真实provider API，不新增付费，不新建/修改Goal。报告与scratch只写各自获准路径，独立venv/node_modules/cache/tmp/基线源；失败/原退出码/DB/journal保留，不删除或新ignore求绿，不宽泛kill。完整相同输入提供双方；不得读取或互传本轮新对方意见。

中文报告必须记录实际任务/session/turn、模型/effort/权限与读回来源、cwd/branch/base/candidate/process/input SHA、全文阅读覆盖及未读项、每个实际命令/退出码/原日志、历史运行/自行运行/静态推断/未验分别说明。逐项处理历史内审1–8、两原指定报告与14行裁定/争议，原严重度保留历史；新问题给固定文件/行号、触发、影响、证据、建议，缺前置与可修代码分别列出但都进入完整结论。

后附政策原文中有通用开发职责及历史排期；它们不把开发写权、建Goal、运行票或旧状态转移给本只读reviewer。controller的review.md仅为排期覆盖核验历史，不能当产品审查通过。

结尾明确“通过／不通过／无法完成验证”及完整原验收是否满足。实际终态、完整报告读回与意见处置才是完成，不以已创建/设置名称/流式片段/局部Pass代替。原两NotPass和P1/P2只由新指定审查依实际证据裁定，owner不先填关闭。
