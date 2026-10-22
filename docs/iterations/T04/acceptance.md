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

桌面操作按现行 AGENTS 执行，互斥资源由总控内部协调。当前组件验证不替代 Electron/App、原生、IPC、生产 CSP、Windows 11 x64/macOS 15 arm64、真人与生产证据；冻结期间仍禁止 HMR 改写受审源文件。

## 总控批准的固定 T09 输入探针

总控后续明确批准固定 Git `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的输入。manifest SHA-256 `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`，版本 `prd-v0.6-learning-1`。实际从该固定提交读取并验证全部 17 项输入与 PRD 来源哈希，原字节复制 manifest/G-base/unclosed-high/conventions 到本线 `tests/fixtures/query/approved-baseline/`，不读取变化中 HEAD，不采用任何 T09 服务/helper/Store。

`test_query_service_approved_baseline.py` 每次重新核对选用文件的 manifest 哈希，再从实际声明 ontology/facts 构建只读标准 RDFLib 图；原始查询与生成查询分别独立还原 G-base，完整预期都为 alarm/A01，单独将 A01 改 Closed 后均为空集合。未用 expected 预填 Store，没有执行规则/行为。此证据验证正式固定输入下的编写互操作，I05 query.execute、任务/取消/游标/范围/Store 联验仍待批准执行器与公共接线。

## 四项 P3 修复验证入口

本轮 name/SPARQL 的固定边界与规范化共用 `tests/fixtures/query/draft-boundaries.json`，两语言分别实际验证；CSV 单测核对完整输出，区分有限真实数值/布尔与字符串公式防护。字段限制、载入重置与非法 RDF 条件另用真实组件 DOM 操作核验：

```sh
node docs/iterations/T04/p3-interaction-probe.mjs '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' unique-run-name
```

探针使用锁定 Vite/React/Playwright 与已安装 Chrome，不新增依赖、不下载浏览器、不启动端口；独立上下文 offline 且拒绝所有请求。`unique-run-name` 须每次唯一，已有原件不会覆盖；运行产物落本树 ignored `test-results/t04-p3-repair/browser/`。这验证真实 QueryPage 组件的五种 DOM 情景，fixture 明确未提供执行/保存桥接或模型服务。实际结果与首失败处置以 status 和验证收据为准。
