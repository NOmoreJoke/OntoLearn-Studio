# T05：规则批次复核的最小接口提案

2026-10-21，总控在原T05功能内增加一项精确文档准备，原oracle准备继续、不撤回或重启。T05仍是唯一机制维护者；I05不得私改固定七模块或新造比较器。仅新增 `docs/iterations/T05/rule-batch-revalidation-proposal.md` 及 `docs/reviews/T05/rule-batch-revalidation-proposal/` 的输入绑定/必要独审/收据，本次不改变20条已收口机制源码/测试/夹具，不复制或执行新产品，不直接授权接口实现。

实际触发是根对I05方案28295b0e的独立静态审查：固定1e3 `check_firing_group` 每次复核会重新校验/编码plan，再计group输入及双份expected/group输出；`evaluate_bound_batch` 是一次plan、整批编码。I05拟同一child执行限额用于fresh compile+所有group复核，可能把合法执行成功的保存批次变成资源失败。I05已实际接受此点并选择请求T05最小批量复核接口/独立预算证明，而非默认每group重置或删除证据。

请依据固定 `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb` 给一个可直接批准的最小方案：

- 精确私有函数/签名、输入/返回/安全失败与所需同进程fresh compile/ProfileValue发行条件；不添加真实图matcher，不声称复核证明全局匹配穷尽或producer授权。
- 固定一次plan与整批完整group/比较/head/source检查的确定性成本与独立、有界复核预算/版本；解释执行成功的合法结果为何能在规定复核范围完整读回，及重复plan/source/编码成本如何处理。不每group重置默认池，不删groups/来源/比较/heads，不用放宽类型/忽略字段换通过。
- 与现单group API及已固定PROFILE/1、mechanism-budget/1的兼容关系，语言与比较政策不变；如需新验证预算标识明确提出，不能默改旧身份。必要产品路径/新测试/fixture精确列出，原20源码各采用/不变或新候选变更逐项说明。
- 针对确定重复计费见证、全部多group/source边界、后项损坏/同进程发行/篡改与整批资源失败的具体测试方案；不从actual生成golden，不在本次docs准备运行机制。
- 实施隔离/本地冻结、原1e3和当前oracle原件保留方式、新候选独审/check/必要包影响与向I05交付的固定路径/hash/消费边界。未知I05数据表示先列精确待答，不并行造第二oracle。

当前oracle独立审查/固定交付优先正常完成；可在不争写文件的独立子任务准备本提案，不为此中断当前计算。完成静态独审、本地docs提交后交总控决定真正最小代码阶段。I05旧C4/新隔离实现许可、future4、正式领域/公共/Store/worker/main/UI等不由本件生效；原无GUI与指定双审/CI/合并/完整父门保留，不重建Goal、不重问已采用Q6。
