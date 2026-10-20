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
