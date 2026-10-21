# T04 精确接线需求与独立交付边界

基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；2026-10-21。

## 已有代码与唯一责任

- `query_service/drafts.py`：有界可视条件 → SPARQL；结构化 RDF 项序列化；保存定义意图的严格校验。没有 Store、图执行或网络调用。
- `renderer/src/query/draft.ts`：私有编辑状态与同一黄金样例。不是 IPC、公共 schema 或新增执行权限；最终公共格式只由 T00 维护。
- `QueryPage.tsx`：独立 React 页面，未改 App/main/preload。catalog/项目身份/保存查询/历史列表必须来自主应用的已批准项目适配器；切项目需按 projectId key 重建页面。刷新结果不会替换未保存草稿。
- `results.ts` 直接复用已批准 `validateV2('result'/'page')`，进一步要求 query kind、断言/断言＋推导范围、完整分页身份及稳定页内顺序；200 行展示/当前页 CSV 导出。不实现游标发行、持久结果或失效规则。

## T00 / I05：正式执行与结果

不修改 `packages/contracts/src/{index,v2}.ts`、`packages/contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json`、main/preload/App/env/style，均留给对应唯一维护者。

1. 现有 `job.create.input` 仅有 snapshot、scope、definitionId、parametersHash、derivedResultIds、preparedPlanRef，没有查询文本或保存查询格式。需批准的业务命名查询草稿准备/执行入口，使原始 SPARQL（包含 editor/model 草稿）实际交给 I05 同版只读＋禁止外联检查；拒绝 `SERVICE`、`FROM`、更新、非 SELECT/ASK、隐式外联。T04 不添加自制解析器或绕过执行器。模板编译探针不能作为外联拒绝验收。
2. `QueryPage.onExecuteDraft` 是内部 UI 事件；收到 draft 与用户选择的 current/historical snapshot，接线者用真实当前项目、快照、定义和参数版本创建任务。不能由 renderer 自报项目授权/历史有效性；历史/推导快照必须由引擎复验身份、状态、实现来源和输入版本。不自动将 stale 推导当 current。
3. 现有 `result.page` 有 binding/rows/cursor，缺少查询列名、RDF term 类型、ASK 布尔结果约定与对应实际执行文本。需在唯一公共 schema/查询结果配置中批准这些元数据，绑定同一 resultId/snapshot/parameters/definition。页面的 result.columns/executedSparql 必须从该权威记录提取，不能把当前编辑器文字冒充实际执行文本。
4. getResultPage/getResult/cancelJob 可复用已批准 bridge；适配器需检查 active project、generation、job/result/snapshot/scope/parameters，丢弃旧项目/旧请求迟到响应。cursor 必须使用引擎真实发行并绑定完整结果身份；不能从 LIMIT/OFFSET 自制 cursor。页面当前仅显示一页，不积累全结果。
5. job.cancel 已受理不能显示已取消；页面复用严格 job 校验，只接收同项目 query.execute；与当前 job 不同的结果明确标为此前结果。失败解释复用现有受限 explainError。需 I05 query.execute 的任务上限/排队/取消/失败/迟到历史、真实 cursor 续页及外联拒绝联验。指定外审前刷新实际 develop 和批准依赖。
6. 局部关系图需要真实 RDF term 元数据；当前通用 cells 只有 string/number/bool/null，无法可靠区分 IRI 与字面量。未擅自把外观像 URL 的值当关系。取得批准 term/列语义后补上适用图；FR-403 此项保持待验。

## T01：查询保存、恢复与失效

不改 `storage.py` 或其他存储/协调器文件。`save_intent` 只返回私有定义意图：family=query/id/expectedProjectRevision/draftDigest/value；不是写入、提交标记或公共 ChangeSet 格式。T01 应由唯一项目服务转换为正式 preview/confirm/commit，并在事务内复验 expected revision。

保存内容完整含 name、description、sparql、scope、capabilityQuestion、source。页面私有 SavedQuery 为 `{definitionId,draft}`；载入后保存回调携带原 definitionId，null 表示新建，保存成功的 Promise 必须返回 T01 真实已持久化 definitionId（更新时须等于原 ID）；同一项目实例/请求/文档选中仍匹配才绑定新 ID，编辑变化继续保留未保存提示，不能靠同名匹配；T01 仍复验正式项目 revision 与权限。draftDigest 仅用于编辑身份，不等于引擎 parametersHash 或执行授权。查询文本/范围、事实、相关推导/规则/本体依赖由现有规则和真实 query dependency policy 派生；不根据模型配置自行加过期原因。重新执行显式选择 current/historical；历史标识持续展示。缓存回收只影响载荷，页面仍显示结果身份并提示重跑。

T01 需提供保存后权威查询读取及同项目/旧基线拒绝、原子失败/撤销、项目包迁移信息。页面保存 Promise 只可在真实保存流程成功后 resolve；未接线默认禁用。不能把本机草稿持久化另设为源真相。

## T08 / T09 / T10

- T08：只提供可见 `modelDraft`；用户查看/编辑实际 SPARQL 和范围后再点击正式执行。该 UI 属性不是模型网关，Python 无密钥。真实 API、零伪造评估和模型失败离线继续由 T08 联验。
- T09：authoring-case.json 使用独立 `urn:t04:` 合成查询探针，测试完整 A01/High/Open 以及 A01 Closed 后空集；不是完整 G-base，不替代 T09 固定全案例/版本/重置。总控后续批准873c8c0固定输入后，本线已按manifest验证17项并用原字节G-base/查询做编写互操作完整输出探针（见 acceptance.md）；未消费T09实现。正式 Q-01/02 仍必须用 I05 query.execute 完整联验。
- T10：当前页 CSV 仅最多 200 行，防公式解释；大结果导出另走授权流程。保存 SPARQL 与 scope/question 等元数据需进入正式项目包并跨设备复现。

## 原父验收保留

FR-400–404、C/D、G Q-01/02/O-01、11–12、全部 P0 与跨模块端到端门继续待验。独立服务/页面、Python RDFLib 标准互操作探针和静态编译不是正式接线、平台验收、指定双模型审查、CI、合并或上线证据。
