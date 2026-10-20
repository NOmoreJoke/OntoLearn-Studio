# I03 候选4双模型审查处置（候选5修订中）

受审 base c2f9b038b23f9f48cdbb8f433a89b55a00edc9d3 → head f574a7234923f28e9356a45a17253803e7602e06。两份报告及必要澄清均经原应用 UI 确认终态；Z GLM-5.3/最高，MM M3.1-Flash/xhigh，均给出通过并允许非阻断意见延期。派发方与总控采用更严格收口：下表已采纳项在 I03 合并前修订，并以新候选重新双审，原通过不继承。原等级、原稿、完整勘误 diff 仍保留。

| 来源/原等级 | 处置、依据与责任 |
| --- | --- |
| MM F1 P2 参数含义未完整覆盖 | 采纳。errors.json 扩齐全部7个含枚举错误码；TS/Python 动态穷举目录，检查码集合、每值含义与非空说明，无任意文本入 wire。I03 完成契约修订；UI 实际文案/安全上下文接入仍属 I04。 |
| MM F2 P2 模板命名误导 | 采纳。RESOURCE_LIMIT→resource.limitExceeded，INVALID_STATE→protocol.invalidState；固定26码和有限参数不扩张，schema/全部正例同步，增加旧 messageKey 负例。protocol.md 明确基于有限参数及可信请求上下文选说明，不从 namespace 推断产生者、不自动重放。实际端到端传播为 I04。 |
| MM F3 P2 标准门禁遗漏新契约/单测；澄清后已证实2处 TS2698 | 采纳，I03 合并前必须修复。根 typecheck 串行 contracts strict、全部 unit strict、desktop；CI 原命令直接消费统一脚本，无 CI/依赖/锁改动。对象夹具经 unknown→非数组对象守卫收窄，未使用 any/ignore/排除新测试。标准 npm run typecheck 对 contracts 和 unit 分别注入真实 TS2322，均 exit2，finally 按原字节恢复，哈希相同；见 evidence/typecheck-gate.json 及原始日志。恢复后完整 check 为最终正证据。 |
| MM F4 P3 未消费错误预算/版本目录 | 采纳。TS/Python 都直接消费 errors.maxEncodedBytes；动态将预算暂改1确认原合法错误被拒绝、恢复后接受。元测试约束版本与 registry/schema id 一致及正整数预算。 |
| MM F5 P3 source→public 映射仅 Markdown | 延期 I04/I05。现有25条可信来源文档仍为规范；需要实际 producer/entrypoint/上下文结构后实现适配器，禁止仅按异常码机械映射未知来源。I03 不凭空增加另一份映射真相。 |
| MM F6 P3 未处理事件终态路径 | 采纳契约澄清，jobs-and-storage.md 给出已有 job.resultRef→result.get→result.page 场景不可变 payload 首行摘要布局；区分 job.succeeded 与队列耗尽，绑定 run/最后快照/消费记录。I03 未实现摘要生成或业务解码；I04 必须实测 E.2/FR701/FR704/G.4 的剩余事件、空队列、失败/取消、缺失/畸形/清理等反例。无新增业务方法、提前停止规则。 |
| MM F7 P3观察、已撤回性能缺陷 | 保留观察。reviewer 合成负载耗时不代表生产性能；无已证实需优化问题。保留守卫，I04/Q5 测量及修复政策承接，不宣称提速。 |
| MM F8 P3观察 readOnlyViewPolicies | 保留观察。comparison/report 是声明性策略，未注册可运行能力；v2Runtime=[] 继续准确表述，不虚构已接入 UI。I04/I05 按既定门槛接入。 |
| Z P3-1 当前不可达双端 fallback 差异 | 部分采纳。两侧元测试限制当前词汇、所有 array 必须显式有限 maxItems，防 schema 演进使差异可达。未来扩词汇/默认上界先统一双端失败行为并复审；当前不扩大适配器结构。 |
| Z P3-2 开库两次全库扫描 | 延期 I04/Q5 真实负载测量，保留现有拒绝损坏身份及零清理证据；不因推测性能风险改 S1。I01 R6 仍维持原等级开放/延期。 |
| Z P3-3 kind 前后空白 | 部分采纳未来服务映射要求：显式白名单映射或拒绝未知，不进行 trim/大小写归并；原内部身份不改写、不合并 current 键。I04 实际映射及迁移反例待接入。 |
| Z 观察1 receiving 与 applying | 保留分层。接收层可识别同会话事件，应用层必须绑定 subscription/job/project 与单调版本；重连须 job.get 对账。I04 实际传输验证，不把纯助手视为运行时保证。 |
| Z 观察2 cancel 响应决策快照 | 接受现有语义，无源码改动。accepted/queued 可以是取消决策线性化时的响应快照，最终持久 cancelled 由 get/订阅读取；不改写历史响应。I04 竞态验证。 |
| Z 观察3 maxActionsPerRound=1000 | 保留 M0 固定上限，无新增可配置自由度；以后调整必须新候选与审批。 |
| Z 观察4 historical 选择仍可读 current | 保留。显式历史读取选择允许可用 current 资源，不强制资源 state=historical；身份/来源/可用性仍须核对。I04 真实读取验证。 |

报告精度：Z 原139行及资源附录/事实勘误完整保存，26/26错误分支、24能力、6冻结输入和12归档源已区分，R6未关闭，prettier忽略报告不当作内容格式通过。MM 原294行和最终339行完整diff保留，F3撤回“全部内容类型正确”，仅源5文件先前实跑strict通过。MM“累计830差分”是审查者累计陈述：派发方读到的最终机器结果仅6条，生成器/若干UI批次存在，但不声称已独立重放830；其完整原始check420/622 exit0已核验。首轮已捕获的原始失败探针/恢复记录保留，未把失败尝试涂改为成功。

本记录不是新候选通过结论，源码/配置/测试/验收的任何修订均须新 head 完整复审。未来运行项的承接不等于缺陷的运行时修复，I03 不宣称协调器/真实图执行/模型/桌面原生/远端 CI 已完成。

归档检查边界：未过滤的git diff --check会标记原始统一diff文件中的空上下文行前缀空格；这些逐字审计产物不做破坏性清理。排除docs/reviews/I03/**/*.diff后全部实际源码/配置/测试/文档无空白错误。原始fullcheck、sources和format完整日志另存revision-validation/*.txt。
