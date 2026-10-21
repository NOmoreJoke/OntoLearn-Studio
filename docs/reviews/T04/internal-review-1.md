# T04 独立内审 1

实际审查 agent：`/root/t04_private_review`；固定 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`、head `4c17a38195982164cf01541fd212c385e558ac7e`。只读审查全部 14 个新增文件及 PRD 对应条款、指南/共同指令，未改文件，未运行 GUI/全套检查。

实际终态：**不通过，需修复 2 项 P2**。

1. **P2 复用后保存丢失查询定义身份。** 原 QueryPage.tsx:31/38/495–501。载入已保存查询后编辑再保存，回调只有 QueryDraft，无法区分更新原定义与另存、不能区分同名查询；Python save_intent 所需 definition_id 缺 UI 来源。建议私有 saved record `{definitionId,draft}`，保留选中身份并传给保存回调，不新增公共契约或 Store。
2. **P2 同项目其他能力任务可被当成查询并取消。** 原 QueryPage.tsx:132/529–535。传入同项目 reasoning.execute 运行任务会标成查询、禁用执行并暴露“取消查询”，点击传出该推理 jobId。审查 agent 以纯内存 TS 转译和 React 静态 SSR 独立复现三项均 true，无写文件无窗口。建议批准 job 校验＋query.execute 限定；当前任务与成功结果不同 job 时标识此前结果。

审查未发现共享文件越权、复制 Store/执行器、模板冒充结果，RDF 项、分页身份和 CSV 防护未发现其他阻断。check 通过来自开发线反馈；本审查不重复全套。真实执行、保存、取消、ASK/关系图、父验收、指定双外审仍待依赖。

## 开发线处置

- R1-01：新增私有 savedQuerySchema/SavedQuery，页面载入保留 definitionId；保存回调收到 id 或 null（新查询），按钮明确新建/更新，提供新建入口。12 项 TS 定向测试中新增同名不同定义 ID 和未知字段反例。
- R1-02：queryJob 复用 `validateV2('job')`，限定 active project 且 capability=query.execute，未通过不暴露取消入口。结果与当前任务 jobId 不同持续标“此前查询结果”；失败解释复用已有 explainError，不回传原始异常。新增真实批准 fixture 变体单测；SSR 独立探针确认其他能力不显示查询/取消、不误禁用执行，query job 正常显示，旧结果明确标识。
- 以上为开发线已实施修复，未自称审查通过；修复候选须由同一独立 agent 重新读取和明确判定。
