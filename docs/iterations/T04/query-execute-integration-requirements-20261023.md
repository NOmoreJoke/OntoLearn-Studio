# T04 正式查询的最小集成需求与现有入口

2026-10-23；只读产品依据 `5070004ec8e3219bea33960bd88f57f1976e9cf8`，共享基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。本文件交 T01/I05/主应用唯一维护者确认接口，不定义第二份 schema、存储或执行入口。进度与接收结论只见 [T04 状态](../../reviews/T04/status.md)。

## 现有入口证据

以下行号均指固定 507，可用 `git show 5070004:<路径>` 复核；此次未运行产品检查。

| 固定源码入口                                                                                                                   | 已有事实                                                                                                       | 接线缺口                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `apps/desktop/src/renderer/src/query/QueryPage.tsx:26,42,489`                                                                  | `onExecuteDraft(draft, selection)` 是私有 UI 回调，返回 `Promise<void>`；current 的 snapshotId=null 是选择意图 | App 未挂载页面；没有正式 execute bridge，也不能从回调返回值取得 jobId                                   |
| `packages/contracts/v2/registry.json:293`；`packages/engine/src/ontolearn_engine/coordinator.py:248`                           | query.execute 仍 design-only；当前 job.create 分派仅接受 test.read/atomic/rounds                               | registry 的声明、job_store 对 query kind 的映射不是可调用业务执行器                                     |
| `packages/contracts/src/index.ts:125`；`apps/desktop/src/preload/index.ts:4`                                                   | 已有 restoreTasks/getJob/getResult/getResultPage/cancelJob 和任务订阅等命名方法                                | 无 execute、查询保存、查询 presentation 获取方法；由唯一 owner 接入，保持 sender/mainFrame/可信文档检查 |
| `apps/desktop/src/renderer/src/query/reader.ts:22,42,66`；`packages/contracts/v2/schema.json:1995`                             | 私有 presentation 要 binding/columns/实际 executedSparql；公共 result 封闭形状没有这些查询展示字段             | 权威来源未接入，不得用当前编辑器文本、模型草稿或 fixture 补造                                           |
| `apps/desktop/src/main/task-service.ts:680`；`apps/desktop/src/renderer/src/query/reader.ts:253`                               | main 从已选项目及真实 metadata 构建 pageBinding；reader 每页复验身份                                           | 需真实查询结果发布及游标链，不能客户端发行 cursor 或只把 job 塞进页面                                   |
| `packages/engine/src/ontolearn_engine/query_service/drafts.py:148`；`apps/desktop/src/renderer/src/query/QueryPage.tsx:46,509` | save_intent 无 Store；保存回调需返回真实已持久化 ID                                                            | 无正式 load-base/CAS、preview/confirm/commit/对账接线；组件 ID/generation 防护不能代替事务              |

源文件身份由旁列 [source-evidence.json](query-execute-source-evidence-20261023.json) 固定。

## I05 已有算法供方与正式接线的区别

总控提供的 [I05 供方事实表](/Users/kyle/Documents/工作/知爻/本体/outputs/20261023_i05_query_execute_supplier_facts/supplier-table.md) 已全文收件，表、receipt、manifest 三份字节/hash 已核；详见 [定点收件记录](../../reviews/T04/i05-supplier-facts-intake-20261023.json)。其事实源为 `9d86ef183b2bfc4d2ac6f1583ceb9a5b29cdf876`，相关 12 函数 AST 与已审库存产品源 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64` 相同；这是供方静态事实，不是 T04 新运行证据，也未 whole-ref 采用该树。

| 已有实际供给                                                                                                                                                                            | 正式接线仍缺什么                                                                                                                                                                                                    |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `semantic.py::query:173` 有真实 RDFLib SELECT/ASK；`semantic_query.py::prepare_lexical_query:146`、`semantic_offline.py::offline:46` 及查询代数检查提供本地解析与外联拒绝               | 项目授权、可信快照、真实 owned worker、硬超时/取消与正式 job 身份；已有 context 拒绝不能升格为 OS sandbox 或完整正式链网络验收                                                                                      |
| `semantic_execution.py::build_request:176/execute_request:331` 真实解码、scope 投影、查询并返回 `{payload,rows}`；payload 含实际 query/queryText、输入/范围/定义/选择及 provenance 内容 | T01 需接完整 payload+rows、实际 capability implementation、结果/终态原子发布与取消/迟到围栏；该内容不自行证明可信 producer、正式 result/job ID 或权威 presentation 来源                                             |
| `semantic_scopes.py::project_validation_scope:234` 支持 asserted 与 legacy selected reasoning 投影                                                                                      | 纯 asserted 查询无需先完成整个 profile producer；这只区分依赖，不缩减所选推导/profile 的完整需求。新 finite7/8 typed profile 仍须其真实受理、来源、reader/pin/累计算额及新只读 scope 接口，不能塞进旧 selected 格式 |

当前隔离供方树的 test-only coordinator/worker 不抹去旧 C4 真 worker 分支的历史证据；T01 正核其可复用性。旧 finite6 通过也不自动成为新 finite7/8 接线证明。完整 FR-400–404、SELECT/ASK、真实网络拒绝、所选范围/推导、历史与保存要求继续保持。

## 唯一 owner 需返回的最小供给

| 依赖与责任                                      | 需要固定的实际接口和依据                                                                                                                                | T04 消费边界                                                                                                                                       |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 正式执行：I05/协调器与命名 bridge owner         | 已批准 ref、真实入口、draft 如何形成执行输入；实际已提交项目/快照/定义/parameters/推导身份；只读 SELECT/ASK、外联拒绝及任务上限/取消策略                | 传经过校验的 draft 和显式 current/historical 意图；接收真实受理 job 并纳入已有 authority/订阅/恢复链，不自报授权或把 draftDigest 当 parametersHash |
| 查询结果 metadata：T01 唯一 owner，I05/T04 消费 | 同 result/job/input/definition/parameters 绑定的实际 SPARQL、SELECT/ASK、列/变量、必要 RDF term、ASK 布尔值及持久来源；计量和固定错误分类由唯一契约确定 | 取得批准权威来源后才构造私有 presentation；ASK=false 不等于空 SELECT，IRI 外观字面量不造关系边                                                     |
| 项目/查询存储：T01                              | 权威 catalog/查询读取、载入时版本依据、保存 CAS、preview/确认/commit、实际 ID 回执、响应丢失按原 operation 对账、恢复/撤销与依赖失效                    | 不在点击保存时用最新 revision 掩盖旧载入；更新保留原 ID，新建用持久回执；切项目/文档及编辑继续变化分别处理                                         |
| 主应用接线：App/main/preload 唯一 owner         | 真实项目选择与 TaskView、命名入口、任务订阅和连接生命周期                                                                                               | QueryPage 按 projectId key；bind/receiveUpdate 使用真实 authority；迟到读废弃，草稿与已执行结果分离                                                |

已有读取侧约束继续消费：project/result/snapshot/scope/parameters 绑定、引擎发行 cursor、每次最多一页及页项上限、跨页排序；cancel ACK 只表示受理，随后读取真实终态。存储 current/stale/historical/evicted 保持权威，历史输入显选，模型配置不自行形成失效原因。具体行号见源码身份文件及既有 [读取接线说明](reader-integration.md)。

## 依赖现状与下一步

供方现状是 **I05 真实查询算法已存在，正式 query.execute/Store 结果 metadata 联验仍待接线与接收**。总控先前提供的可定位 T01 stageParent 为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-C1-complete-zcode-review-244207d`、固定 `244207d0928db9ed1d47a3ccb2e91da4ebbfeb21`，不等于正式查询供给已批准。类型桥接源提案在 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-typed-bridge-source-proposal-20261023`，先前回执时尚未冻结新 candidate、首轮 lint 失败修复中；最新调度要求 8.3 先冻结、不混新功能。这里只记录总控回执，不读取或接入这些未批准实现。

F-R3-01 保持原 P3/非阻断/未修未关；T01 已接未来统一责任，**延期至正式结果 metadata 的度量及错误分类契约冻结后处理**，T04/I05 按该契约消费。draft D1 不扩为结果计量政策。OBS1–6 及零列/ASK 等已有边界继续保留，不新增默认答案。

取得精确供方回执后才固定后续独立集成候选及实际文件责任。第一条真实链应覆盖：真实项目输入 → 用户显式执行 → 本人 query job → 权威执行文本/metadata → 实际分页；再接保存/恢复及失败边界。既有 `82630f50def6aac2a5ba60470757791dd39053db` 的 16 个 owner 讨论样例继续作为待确认输入，不另造替身或重复 S1。正式链仍按 FR-400–404、附录 C/D/G 的 Q-01 完整 A01、Q-02 完整空集及既有取消/游标/外联/历史/保存边界验收，验证只随真实接线改动执行。
