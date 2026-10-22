# QueryPage 固定 507 消费小包

供 T08/T01 后续按成熟实际接口接线。唯一产品源为 `5070004ec8e3219bea33960bd88f57f1976e9cf8`，批准 base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；该完整有界 S1 已获总控有限接收同版双方 Pass。本文只描述该版本既有消费口，不使用后续 live 11371B 需求稿作为产品或契约依据。当前进度见 [T04 状态](../../../reviews/T04/status.md)。

[manifest.json](manifest.json) 列出 5 个本线源码的精确路径、Git blob OID、SHA-256、字节/行数和可读固定 ref；`sources/` 中对应 `.txt` 是逐字原件，供阅读，不从 docs 导入执行。另列 16 项共享依赖/宿主上下文的固定 blob 身份，未复制或修改共享实现。读取某文件可用 `git show 5070004ec8e3219bea33960bd88f57f1976e9cf8:apps/desktop/src/renderer/src/query/QueryPage.tsx`，其余以 manifest 的 `fixedReadableRef` 为准。

## 源码与依赖

| 本线文件（前缀 `apps/desktop/src/renderer/src/query/`）                        | 用途                                                                                                          |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| [QueryPage.tsx](sources/apps/desktop/src/renderer/src/query/QueryPage.tsx.txt) | 页面；直接导入 draft/results、`../task-presentation`、contracts 的 JobView、React 和 query.css；不导入 reader |
| [draft.ts](sources/apps/desktop/src/renderer/src/query/draft.ts.txt)           | 私有 QueryDraft/SavedQuery/VisualQuery 校验与编写；zod；不授予执行、事务或 IPC 权限                           |
| [results.ts](sources/apps/desktop/src/renderer/src/query/results.ts.txt)       | 使用批准 validateV2 校验 query metadata/page/job；有界当前页 CSV，不发行 cursor                               |
| [reader.ts](sources/apps/desktop/src/renderer/src/query/reader.ts.txt)         | 可选的只读消费适配；依赖四个现有命名 bridge、TaskView/TaskUpdate；不是 executor、writer 或订阅 owner          |
| [query.css](sources/apps/desktop/src/renderer/src/query/query.css.txt)         | 由 QueryPage 的 CSS import 加载；两列布局，760px 以下一列；页面容器有颜色 fallback                            |

固定 runtime 声明为 React/react-dom 19.3.1、zod 4.6.7；workspace contracts、现有锁和 JSX/DOM/Bundler/JSON 编译上下文见 manifest。`task-presentation.ts` 使用包根 `@ontolearn/contracts`；query 模块的 `validateV2` 使用源码相对路径 `packages/contracts/src/v2`，不能误换为 package 的 `/v2` design export。保持仓库相对路径，不将 5 文件平铺后假定可编译。本次不安装依赖或做新构建。

宿主 `main.tsx → style.css → tokens.css` 是现有样式上下文；query.css 不是 Shadow DOM 隔离样式，部分类选择器没有 `.query-workspace` 后代限定，宿主全局控件样式也会参与。原 OBS-3 保持，由实际 App 接线核布局/样式，不在此改样式、共享 token 或 CSP。

## 真实 props 与 callbacks

准确声明见 QueryPage.tsx:26–49 的原件；以下是消费含义。

| 输入                                             | 固定 507 类型与含义                                                                                                                                                                              |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 必需 `projectId`、`catalog`                      | projectId:string；catalog 为 classes/predicates 的 `{iri,label}[]`。由项目 authority 提供，父组件按项目身份 key 重建；不是 renderer 自报授权                                                     |
| `historicalSnapshots?`、`alarmVocabulary?`       | 前者 `{snapshotId,label}[]`；后者 `{alarmClass,severity,status}`。只提供真实已批准选择/词汇，模板不产生结果                                                                                      |
| `modelDraft?`、`savedQueries?`                   | QueryDraft 与 `{definitionId,draft}[]`。modelDraft 经用户点“查看”并校验后进入可见编辑器，不自动执行；保存记录仍不是 CAS/事务 authority                                                           |
| `job?`、`cancellationRequest?`、`resultLoading?` | JobView；`{jobId}`；boolean。仅同项目 query.execute job 可展示；取消标记须绑定同一 job，不冒充 cancelled                                                                                         |
| `result?`                                        | `{metadata:unknown,page:unknown,columns:string[],executedSparql:string}`。这是私有页面输入；metadata/page 仍经批准 validator 与绑定检查，原执行文本不能用当前编辑器或模型文本补造                |
| `onExecuteDraft?`                                | 签名见下。current/null 是选择意图；回调不返回 jobId。正式受理后仍须把真实 job 放回 authority/任务链；无回调时执行按钮禁用                                                                        |
| `onSaveDraft?`                                   | 签名见下。只在真实保存流程成功后返回 persisted ID；更新 ID 不变。同 request/documentGeneration 才回填；编辑变化保留提示。无回调时保存禁用；组件不提供 revision/CAS                               |
| `onNextPage?`、`onCancelJob?`                    | 分别 `(cursor:string) => Promise<void>`、`(jobId:string) => Promise<void>`。使用真实发行 cursor/本人 job；无回调动作禁用。reader 的 Promise<boolean> 不是这两个 Promise<void> 回调的直接同型替代 |

两项回调的准确签名（QueryPageProps 原声明）：

```ts
onExecuteDraft?: (
  draft: QueryDraft,
  input: { selection: 'current' | 'historical'; snapshotId: string | null },
) => Promise<void>
onSaveDraft?: (draft: QueryDraft, definitionId: string | null) => Promise<string>
```

QueryDraft 固定字段为 name、description、sparql、scope（asserted/asserted+derived）、capabilityQuestion、source（template/visual/editor/model）。draft.ts:55–81 的 name/SPARQL 是原串 UTF-16 上限 128/65536 后按固定边缘空白集合规范化；这是已审 draft 行为，不扩展为结果 metadata 政策。新建/成功载入 saved 推进 documentGeneration；成功载入 model 清空 visual、保留原保存身份/generation；此包不改变这些语义。

## 有限 reader 契约

`QueryResultReader` 只需要 `getResult/getResultPage/getJob/cancelJob` 四个批准命名方法。`bind(TaskView)`、`receiveUpdate(TaskUpdate)` 接真实主应用 authority，generation/project/snapshot/revision 改变会废弃旧读取；不自行 subscribe。父应用仍负责 restore/订阅/断连生命周期与自身订阅释放。

`read(QueryPresentation,pageSize=100)` 接私有 `{binding,columns,executedSparql}`，binding 为 projectId/resultId/inputSnapshotId/scope/parametersHash 加 `order:'ordinal+rowId:asc'`；必须来自后续批准权威来源。页大小 1–200，每次先 getResult 核身份再 getResultPage；`nextPage` 仅收当前实际 nextCursor，保持跨页排序锚，不累计全结果。`snapshot()` 是复制的可丢弃显示态；loading/ready/error 与安全错误需父适配器实际映射。

`refreshJob`/`cancel` 只接受同项目 query.execute job。cancel 先重读、去重并检查版本；ACK 只记录请求及最低版本，随后重读真实状态；终态由后续真实观测确认。`dispose()` 废弃回调，不自动取消 worker。reader 不执行、不保存、不发行 cursor、不自动重试。

固定 cells 仅 string/number/boolean/null，现有接口没有可直接消费的 typed RDF term 或 ASK 专用页面形状。不能把 I05 payload/rows、N3 字符串或 AgentSidebar 内容直接充作 presentation，也不按字符串外观造关系。原 F-R3-01 的 reader/页面长度差异仍未修，已延期至 T01 正式 metadata 度量/错误分类契约冻结；此包照录既有源，不自定统一政策、ASK/零列默认答案。

## 时间与接线边界

固定 507 的 App 未挂载本页，且当时该树 coordinator 分派仅 test 能力；这是版本事实，**不是历史上没有真实执行器**。总控已另发 T01 asserted 后端票，正核旧 C4 真 worker 的复用；本包没有核其新实现、接收其完成或扩大为 public presentation/App/draft save 授权。T08 新 e3 的实际 DOM 证据只挂 AgentSidebar，不等于 QueryPage 或 I04 真实取消链。

未来由实际成熟接口决定 T08/T01/主应用与 T04 的适配文件责任；本包不新增 schema、命名执行入口或自造展示数据。完整 FR-400–404、selected/profile、SELECT/ASK、真实网络拒绝、历史、保存和现有父缺口保持。此次仅 Git 原件提取与文档/身份核验，无新产品测试、GUI 或指定双审。
