# I05 独立阶段内部审查与处置

2026-10-20。内部只读 agent：`/root/semantic_boundary_review`。模型沿用当前 Codex 设置，未冒充指定第三方；未启动 GUI、未修改实现或构建环境。设计审查后按实际发现修复并定向复核，没有固定轮数通过规则。

| 编号 | 实际发现 | 处置与验证 |
| --- | --- | --- |
| I05-IR-01 | SAMPLE/GROUP_CONCAT、无序切片和数值同值不同 datatype 排序导致跨 hash seed 差异 | 候选只保留 COUNT 聚合；拒绝 LIMIT/OFFSET；无序完整结果规范排序，直接投影变量 ORDER BY 以 RDF 词法/类型打破同值 ties。seed 1/2/5 独立进程复核一致，回归通过。 |
| I05-IR-02 | label/comment 经 domain 公理或规则产生类型，违反 C 边界 | 注释事实不参与 domain/range 闭包和规则匹配；真实反例关闭。 |
| I05-IR-03 | 规则可生成 subclass 公理或绑定任意谓词 | 入场及绑定后都限制为领域属性/类成员，禁止 schema 输出；未匹配规则同样拒绝。 |
| I05-IR-04 | REGEX 原始异常、非法规则字段/term、Unicode surrogate，以及 RDFLib 词法原值诊断 | 查询求值映射 QUERY_FAILED；先校验规则结构和 term 再调用 Graph.add；Unicode 编码错误映射 INVALID_UNICODE；按执行上下文过滤 rdflib.term 原值日志，其他上下文不变。新增反例均为固定 SemanticError，无原值日志。 |
| I05-IR-05 | 相同路径和组件的多个 SHACL 约束无法区分 | 真实报告增加 sourceShape，双约束完整身份回归通过。 |
| I05-IR-06 | S1 负载没有 RDFS 扩张，所谓 Cold 已经执行原查询 | 保持原 S1 口径，另加四条 ontology 并核对完整 9/81 个 RDFS 结果；改名 FirstAfterS1，独立 startup 测新进程导入至 ready/退出；不宣称 OS 冷缓存。 |

主开发补充实测 SUM 浮点归约：同一 `1e16,-1e16,1` 在不同 seed 得到 0 或 1。统一聚合白名单后，内部 agent 确认 SUM/AVG/MIN/MAX 均明确拒绝，COUNT=3；补充定向 10 项通过。最终完整语义回归 89 项，随全库 287 项 Python 验证通过。

额外边界已采纳：用真实 Validator 绕过通用入口的全局布尔 patch；拒绝 SHACL 数据范围混入 subclass/domain/range，因为 inference=none 仍可能扩大 targetClass；增加累计工作/证据预算。内部 agent 明确原六项在当前实现层关闭；未将其结论延伸至未运行的原生集成、包体或指定双审。

包内测量与许可由主开发实际执行，见 [同版独立证据](../../iterations/I05/independent-v2.json)。完整 I05 状态与剩余门禁见 [status.md](status.md)。


## v3 补充的独立审查

总控补充要求后，独立 agent 只读复核了 Q6 逐项差异、真实两范围、内部细码与首次工作负载；后续按真实发现定向复核，不设置固定轮次。此补充审查仍不替代 ZCode / MiniMax 指定全范围双审。

| 项目 | 实际发现或检查 | 处置与证据 |
| --- | --- | --- |
| 验证范围 | 纯投影最初没有转交规则链警示；丢警示会使执行语义说明不完整。 | provenance 保留完整 warnings；R-risk＋R-next 真实结果保留链提示且无二阶事实。单元与共享源码 / 包内样例核对。 |
| 原始结果 | 分图不能通过删掉传递公理或派生类型实现。 | ValidationScope 的 facts 保留全部原断言；另以 reasoning_result 原样返回完整 reason() 输出，含 RDFS 公理与类型、规则结果、依据和警示。facts / ontology 是另附投影视图，不改写原推理输出。独立 agent 最后定向复核 scopes 14/14，通过完整字典等值和输入图不变测试。 |
| 两范围目标 | 必须证明真实 Validator 的 targetClass 集合确实不同。 | 同一完整约束图在 asserted-only 和 selected-derived 的所有命名形状目标集、两项名称违规、path / component / sourceShape、补名后重验逐项核对；复制形状图后调用 Validator，避免其内部 ShapesGraph 修改共享输入。 |
| 类型错误与范围错误 | 非 str 不应被归容量；合法但不支持类型与非法词法不能混淆；中间匹配不是最终结果。 | 固定细码与真实分支回归分离；超大有限 Decimal 使用 is_finite。形状 targetClass / datatype / path 的已知非法项单独细分，未分类匿名路径安全兜底，不误称合法范围外路径。公共分类交 I03 唯一维护者。 |
| 首次工作负载 | 原 FirstAfterS1 已执行 S1 查询，不能代表首次真实候选工作。 | 单独 fresh 入口先首次 parse / query / reason / SHACL，立即 flush firstComplete，然后 warm；父进程首行到达与 warm / 退出分开计时。独立 agent 实跑 source 1x / 10x 检查时序及空 stderr；最终源码与包内重复由主开发执行。 |
| Q6 | G 最小样例通过不能证明全部 FR-505。 | 12 行差异表明确比较运算 / 同规则多结论未覆盖、查询与模板的候选收窄及逐项待决定，不代替本体＋技术负责人批准。 |

补充后语义测试 124 项通过，含 scopes 14 项。独立 agent 未构建最终包、未运行真实任务系统或 GUI；最终打包与全库验证按 [v3 证据](../../iterations/I05/independent-v3.json) 记录。原 v2 的 89 项结论和原始测量保持历史，不倒写成已经覆盖新分支。


## v4 指定已有结果投影的独立审查

本轮由同一独立只读 agent 审实际纯入口、匹配 / 来源边界和真实反例。初始162项语义测试通过仍未覆盖下列两项；据此补反例修复后定向关闭，不把原通过当成这些新边界的证明。

| 实际发现 | 处置与复核 |
| --- | --- |
| `_from_n3` 默认规范化使真实 reason 的 `Literal("01",xsd:integer,normalize=False)` 被投影器误拒，亦可能改写原词法视图。 | 固定内存 Turtle SinkParser，局部 RDFSink.newLiteral 使用 normalize=False；不切换全局规范化或 boolean converter。真实 integer01、decimal1.00、boolean、语言及中文 / 转义值 native/JSON 回归，独立 agent 实测原反例关闭。 |
| 损坏所选载荷中的 surrogate 进入最终摘要，抛裸 UnicodeEncodeError。 | 每行解析前UTF-8可编码性检查并转换固定 REASONING_RESULT_INVALID；原输入/规则摘要编码错误转固定 INVALID_UNICODE。独立 agent 实测两类安全错误，原项关闭。 |

设计复核指出：规则实际可读集合还包括原 ontology，不能由投影器暗删；实际 ontology 条件正例已通过。完整结果和依据覆盖、重复变量、生产计划、冻结输入、schema角色、警示与多依据按真实有限语义检查；全局推理完备性 / RDFS证明真实性仍不在该一致性检查内，不通过重算补齐。展示来源独立复制，原选中载荷保留原对象。私有生产上下文摘要不声称授权 / Store / 不可变ID验证。

最后补入版本 i05-finite-3、共享包内的真实01词法样例及最终分图预算反例。完整语义172项，新增指定投影48项；最终全库及真实包证据见 [v4清单](../../iterations/I05/independent-v4.json)。内部复核不替代指定全范围双审或真实I04联验。


## e45 基线纯错误适配器审查

总控 / I04 明确交接后，独立 agent 先读已批准 I03 规范并复核 producer / stage / origin 设计，再只读审实际新适配器和 golden DTO。该内部审查不替代最终全 I05 两指定模型的新全范围审查。

开发自查先补出两处实际阶段偏差并保留失败：constraint 文档的 INVALID_TURTLE 应固定 syntax，query 的 INVALID_UNICODE 应按真实 query 入口分类。修复后专用193项通过；不是把原通过当成新增反例已覆盖。

| 独立实际发现 | 修复与复核 |
| --- | --- |
| 已知细码配对阶段过宽：REASON/SYNTAX 可报 ruleOutput，QUERY/SYNTAX 可报查询结果预算，REASON/SYNTAX 可报 RDFS结果预算。 | 内部理由×producer×stage 精确白名单；TEXT / GRAPH 输入阶段也分开。三项原反例及同类错配安全 Internal。 |
| 只核对命中的 const 分支不足：追加 code 为 enum 的重叠 Internal oneOf 分支，或 error 根加入未知关键字后仍能构造，实际 owning checker却拒绝DTO。 | error 根封闭为oneOf；全部分支必须唯一const code并和catalog codes集合、四字段规范严格对应。重复 / 非const / 根未知字段拒绝，不再输出不符合注入规范的DTO。 |
| parameterMeanings 同值list误被当作有效字典。 | exact dict、枚举键一致、非空字符串定义；损坏配置固定本地配置错误。 |

独立审查的6个新触发用例修复前真实6failed/193passed，修复后208passed，原始日志均保留。补充细码1–64字符的精确匹配门、不trim；输出恰好2048bytes可接受，多1byte的配置拒绝。messageKey / retryable来自注入且一致的canonical目录，返回对象 / 枚举spec与外部输入隔离。独立agent最后复现三项关闭，208/208通过，未发现同类新增问题；未修改文件或操作GUI。

完整check / 相关回归和精确来源记录见 error-adapter-e45.json。仅证明纯分类器和规范DTO，不证明producer真实性、授权、immutable资源、Job/bridge/UI传播或当前包内调用。


新基线首次完整check的424项TS、类型与build已过，随后Ruff发现接口文档Python代码块的import格式未展开；仅修正本线文档，保留首次失败日志，再完整运行check。最终424TS / 1006Python（208adapter）及sources12通过；未借此重跑旧包或旧测量。

## 正式 I04 基线集成内部独立审查

只读 agent `semantic_boundary_review` 全范围复核原B1/附录C/D/E/G及真实运行边界；写入子任务分别在独立execution/bridge/native worktree提交，最终主线统一集成，没有共享文件争写。原适配器208 golden保持，不把内部审查替代指定模型审查。

实际发现与处置：公开1024帧限制被误套私有worker通道→私有固定262144且真实1024公开协商反例通过；合法saved ontology超范围构造被标可信Internal→用户输入语法入口真实Unsupported并保留可信错层Internal；大字面量/规则在REASON阶段错误归类→实际Turtle输入预算semanticInput，disabled规则不计执行预算；validationBinding补充后结果行超过10000冒泡引擎退出→最终完整投影边界安全RESOURCE_LIMIT semanticResult。29项真实worker/stdio/Store联验及全库1511Python含相应反例，37项窄bridge及全库672TS通过。独立agent最后未确认新增阻断，验证范围按实际运行报告，不冒称其亲跑完整包/native或指定双审。

Linux有效原生2×2及打包入口ready门槛修正另见 [C1证据](integrated-c1-verification.md)。所有历史失败与成功原始日志并存，源/包精确绑定，不改写旧检查的候选归属。

最终证据只读复核逐字读取全部raw清单、重算SHA与计数，验证117份原证据及13份最终native raw；两平台suite完整result/network相等、portable stdout逐字相等、实际stdio各1passed、C4各17passed、全库672/1511。逐窗口完整results/project/jobId+operationId直接比较相等，不只信任摘要。指出117清单不能统指851最终native的文案归属，已改为分别链接原清单与sealed清单。其后sealed第14份仅补存已通过的851静态检查原log，由主线重新核验所有14份SHA；无产品/测试/验收改变。未发现新增产品阻断；Q6逐项仍待决定，不替代指定全范围双审。
