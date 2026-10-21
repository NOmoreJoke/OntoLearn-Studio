# T04 后续真实接线输入

状态：交唯一维护者讨论，**不是已批准接口或实现**。仅在独立 `T04-query-integration-next` 树准备；冻结 T04-S1 的 `554ec89` 实现和 `19ef252` 证据不变，不新增 Goal。

## 责任与已有证据

2026-10-21 已全文读取共同指令新 SHA `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39` 及 I06→T01 八文件生效交接。T01 唯一维护 storage/格式 Python4/canonical-main8；I06 维护余六个接线/UI；T03 维护依赖构建四。这里只提出输入和完整预期，不改任何共享文件，不读取/复制其未批准实现。

批准 `5f910b5` 的 `Store.commit` 事务中再次检查 base revision；正式 query 仍 design-only。S1 固定 `554ec89` 的 `save_intent` 要求 expected_revision，但页面当前私有 onSaveDraft 只传 draft/definitionId，载入记录也未带正式版本回执。这在 S1 明确排除的持久化/桥接范围内，不能被 S1 通过证明安全保存已接通。

## 需要 T01 固定的保存语义

载入查询时应取得并保留其真实身份、版本/输入依据及工作区 generation。实际方法名、CAS 粒度和回执由唯一 canonical 决定：可以使用经批准的全项目 base 或明确的更细 query/app CAS，但必须证明旧内容不能被点击保存时取得的“最新版本”掩盖。项目切换、另一查询载入和保存期间继续编辑必须分别处理。

保存应经唯一 preview/确认/commit/对账流程。提交确认前复验实际基线；首次创建成功返回真实已持久化 ID，后续更新原 ID，同名不合并。响应丢失须以原 operation/marker 对账，不把异常当“未提交”，不盲目新建第二查询。当前 S1 对 ID/generation 的保护只能在收到真实回执后生效，不授权 renderer 发行 ID 或直接写 Store。

FR-404 要求名称/说明/SPARQL/范围/关联能力问题完整保存；FR-006/D 要求保存视图过期和历史显选。查询文本/范围更改、上游事实/相关推导变化按唯一依赖规则处理，模型配置不得被客户端擅自映成过期原因。真实 ChangeSet/恢复/撤销与持久回执须由 T01 在同版输入中验证。

## 需要执行器/公共结果固定的展示语义

每个实际结果必须可追溯实际已执行 SPARQL、SELECT/ASK 形式、列/变量及必要 RDF 项类型，并绑定项目、result/job、输入快照、范围、参数和查询定义来源。编辑器后来改变的文本、模型草稿或独立模板不可替代执行原文。

现批准 page.cells 只有 string/number/bool/null，无法证明字符串是 IRI 还是 IRI 外观字面量；实际 ASK=false 与 SELECT 空页也不能靠行数区分。需由 canonical 同版明确这些真实元数据来源；S1 的内部 presentation 只是消费口，不是第二份协议。取得真实 RDF 类型后才实现适用的局部关系图，不能按 URL 外观造边。

历史/过期/载荷回收、当前推导与所选输入不匹配、错 result 游标及取消 ACK/终态分别呈现。网络/只读策略只由批准真实执行器落实，不用文档样例或模型推断代替执行。

## 完整对接样例与需回执项

[owner-discussion-cases.json](owner-discussion-cases.json) 含 16 个合成观察/完整预期：创建/同名 ID、旧载入和旧预览冲突、提交后响应丢失、切文档迟到回执、保存期间继续编辑、范围变化失效、实际原文与现编辑器分离、错结果展示、ASK 与空 SELECT、IRI 外观字面量、stale 推导、旧游标、历史载荷回收和模型 SERVICE 草稿拒绝。它不包含可调用方法、JSON Schema、注册表、第二 writer 或测试替身执行器；字段记号等待 owner 统一。

请总控协调 T01/实际执行 owner 回执：保存 load-base/CAS 和 commit receipt 的单一实际字段；真实 query execution/presentation 来源及错误；何时形成可批准同版候选。只有实际批准后，T04 才在独立后续候选适配页面/服务并真实联验，刷新 develop、必要验证、指定双新完整审查及远端门。该讨论不重开未变 S1，也不关闭 FR-400–404 或父功能。
