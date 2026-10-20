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
