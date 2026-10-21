# T04 原需求与验收入口

本线的执行状态以 [status.md](../../reviews/T04/status.md) 为准；本文列验收对应关系与命令，不代表已通过。

| 需求   | 本线独立入口                                                         | 正式验收不能省略的部分                                                       |
| ------ | -------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| FR-400 | alarmTemplate、compileVisual、SPARQL 编辑、modelDraft 可见载入       | 已批准执行器完整 Q-01/02；T08 真实自然语言草稿；离线无 API 操作              |
| FR-401 | scope 持续显示、当前/历史输入选择、resultNotice、实际 executedSparql | snapshot/derived/project/parameters 身份由主进程与真实引擎校验；历史不混当前 |
| FR-402 | 无本地执行替身/网络；200 行结果校验及当前页展示                      | I05 SELECT/ASK、SERVICE/FROM/更新/隐式外联拒绝，真实任务时限/取消/cursor     |
| FR-403 | 表格、当前页 CSV、空页方向、纯文本渲染                               | 实际完整集合与导出；真实 RDF term 支持下适用的局部关系图；O-01 未记录语义    |
| FR-404 | 完整查询草稿字段、保存意图和复用页面                                 | T01 preview/confirm/commit、读取恢复、过期、撤销、历史显选、T10 跨设备复用   |

## 无窗口可运行命令

在本线 worktree 运行：

```sh
npm ci --ignore-scripts
uv sync --frozen
npm run check
uv run --frozen pytest packages/engine/tests/test_query_service_authoring.py -q
npx vitest run tests/unit/t04-query-authoring.test.ts tests/unit/t04-query-results.test.ts
node docs/iterations/T04/ssr-probe.mjs
```

只在实现变化、失败或待解风险时复测相关项。`npm run check` 由批准 AGENTS 要求，覆盖 lint/format/types/vitest/build/ruff/pytest。没有引入依赖或打包配置，无需为本独立编写代码重复包内引擎验收；真实执行依赖接入后执行其对应包内同样例验收。当前不改归档资料，不改 source manifest。SSR 使用当前锁定 TypeScript 与 React 在纯 CLI 生成静态 HTML，不启动浏览器、Electron、端口或应用，不验证互动、CSS/CSP、下载、原生或性能。

## 合成编写探针的完整预期

`tests/fixtures/query/authoring-case.json` 固定词汇、条件、SPARQL、三条合成告警、完整预期行；Python 用 RDFLib 实际验证标准查询语义，TS 核对同一生成文本。A01/High/Open 是唯一结果，A02/Closed、A03/Low 均不能混入；独立还原后 A01 改 Closed 得空集合。它与 G-base 使用不同命名空间，只验证 authoring 互操作；完整 G-base 含设备、本体、规则和行为等，由 T09 维护，不从本探针推断正式 Q-01/02 已通过。

## 正式同版候选顺序

只消费已批准 I05/T01/T00/T08，刷新真实 develop，完整联验所有父功能与跨模块条款后固定 base/head。由当前开发聊天预约并通过 ZCode GLM-5.3/最高和 MiniMax M3.1-Flash/xhigh 各新独立完整任务，全文读回并逐项处置。门禁通过才 push/PR（attach），实际 CI 通过后正常合并 develop 并核验远端/保护原件。服务单独合并不关闭父功能或上线门。独立 Codex 内审不替代这两个指定模型。

本机不运行 Electron/e2e/native/HMR/凭据提示/审查应用，不抢焦点；这些验收仍须隔离环境或已有明确时段授权。Windows 11 x64/macOS 15 arm64、用户验收和生产状态不能由这里的 CLI 证据替代。
