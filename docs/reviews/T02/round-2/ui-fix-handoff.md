# T02-S1 UI 首轮意见修复交接

本线起点 `6ad61d7f15b64b312ba253418af1edc16cfb8615`，功能原基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，保留原 `4932122` 产品。分支 `feature/t02-s1-ui-review-fixes`；独占工作树 `.worktrees/T02-s1-ui-review-fixes`。本记录只交接 UI 子任务，不取代模块状态或新候选审查。

已读当前 AGENTS、PRD V0.6 FR-200–204 与附录 C/D/G、原 `acceptance.md`、两份 `round-1/received-20261022/*/report.md` 及 `triage-initial.md`。未改 Python、公共契约、App、bridge、依赖、配置、原验收或首轮报告。

## 具体处理

| 意见 | 本线实际改动与证据 |
| --- | --- |
| M-P3-1 | 页面删除影响和 Diff 引用影响明确为“基准快照（项目版本 N）中的引用；包括本次修改计划将解除的引用”。保留基准引用语义，不改成候选空集合。headless 核对引用内容、版本和 delete 请求基准；服务批量解除完整集合由 Python owner 处理。 |
| M-P3-2 | 去掉未发出的 `EditIntent.copy`，注释明确复制定义到可编辑新表单，修改后发送完整 `create`，页面不持久记录复制谱系。headless 分别复制 class/objectProperty/dataProperty/individual，全对象比较 metadata（classType、labels、definitions、synonyms、examples、parents、domain、range、types）及复制后修改。 |
| M-P3-3 | 原 11 项检查保留；追加至 21 项逻辑检查。25 对象按完整排序集合断言第一页20/第二页5、页码、按钮边界和返回第一页；搜索重置与空集合；复制后编辑、清空新建；assert/retract 精确事实和基准；版本推进保留草稿并阻断直至显式重读，切项目清空并重绑；错误固定文案；图截断和完整可见边集合。均为真实 headless 交互，无 SSR 替代。 |
| M-P3-4 | 页面 `useMemo` 只依赖 tab/objects，表格或图页不计算类树；classTree 建 parent→children 索引，保留排序、闭环、多父、缺失父引用与重复边处理。原测试保留，新增完整序列测试。未测量性能变化，不声称整体 O(n) 或容量提升；祖先集合、边和排序仍有成本。 |
| Z-P3-4 | `update<K extends keyof ObjectRow>(key: K, value: ObjectRow[K])` 约束字段和值，classType select 只接收 rdfs/owl。 |
| Z-P3-5 | 事实表单增加规范 n3 单术语示例和“预览服务检查格式和语义”。真实输入坏值后，合成服务拒绝路径对 assert/retract 均核对固定错误文案且无成功预览；未引入第二 RDF parser 或公共 schema。此项只证明页面呈现，不证明真实引擎拒绝或 IPC。 |

`T02_UI_OUTPUT_DIR` 是 check.mjs 可选输出目录；未设置时仍使用原默认路径。本线始终设置自有输出目录，未覆盖历史 JSON/截图。fixture 扩为25个有完整元数据的对象，RDF呈现数据同步对应，合成 callback 仍不产生 Store/IPC/e2e 证据。harness 对 authored JSON 的 tuple/kind/classType 显式收窄仅限测试文件。

## 实际验证

本树 `npm ci --ignore-scripts` 独立安装440包，exit0，未借用其他树 node_modules。没有执行 Python 用例或建立共享 uv 环境。

| 实际命令 | 结果 |
| --- | --- |
| `npx vitest run tests/unit/t02-ontology-views.test.ts` | 4 passed / 1 file，exit0 |
| `npm run typecheck:unit` | exit0 |
| `npm run typecheck --workspace @ontolearn/desktop` | 最后一次 exit0 |
| harness 单文件 `tsc --noEmit`，完整参数见 `typecheck-harness-2.result.json` | exit0 |
| 定向 ESLint（两源文件、单测、check.mjs、harness.tsx） | 最后一次 exit0 |
| 定向 Prettier check（6个改动代码/fixture文件） | 最后一次 exit0 |
| `node docs/iterations/T02/ui-probe/check.mjs`，显式指定既有1234执行器和本线输出目录 | 最后一次 headless-4 exit0，Chromium151.0.7922.34，25对象/21项逻辑检查；原11项保留并通过 |
| `git diff --check` | exit0 |

执行器实际路径：`/Users/kyle/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell`。下发的 `chrome-mac-arm64/headless_shell` 路径经核对不存在，未尝试启动。探针通过 route.fulfill 提供本地静态构建，无 HTTP 服务或监听端口；未启动 GUI、Electron 或 native。

## 首失败与保全

- `headless-1` exit1：原第11项移动端无横向溢出断言发现新增长URL提示溢出，前10项通过。原 stdout/stderr、failure JSON、两尺寸截图和该次构建产物均独立保存。以页面既有 code 换行样式修复，未删除断言；后续 headless-2/3/4 全过。
- `typecheck-harness-1` exit2：扩大后的 JSON fixture 多语言数组尚未显式收窄为二元组。原完整 TS2352 日志保留；harness 改为显式 tuple/kind/classType 收窄，typecheck-harness-2 exit0，随后 headless-4 全过。
- 每次运行使用独立编号 stdout/stderr/result JSON，不覆盖失败。headless-2/4 两尺寸截图字节相同，已读取两张本线截图检查布局；最终对应结果在 headless-attempt-4。

## 证据与边界

本树本地证据根：`test-results/t02-s1-r2-ui/`。`before-hashes.json` / `after-hashes.json` 保留前后哈希；各次 headless 输入另存 hash；`evidence-manifest.json` 列出原始流、结果、截图与构建产物的 bytes/SHA256。原 `docs/reviews/T02/ui-probe.json`、原验收、两锁文件、build.mjs/index.html 和携带的当前 AGENTS 均与开始时字节一致。仅本任务精确路径进入提交；AGENTS 未暂存。

按父任务分工，本线未跑全仓 check；父整合后统一执行并审查实际新候选。没有运行 IPC/Store/真实引擎拒绝、e2e、打包、生产、双平台、模型、CI、push/PR/merge；不得继承原493双审通过结论。原首轮报告与历史证据保持。

最终关键证据哈希（均位于上述本线证据根）：

| 文件 | bytes | SHA256 |
| --- | --- | --- |
| `headless-attempt-4/ui-probe.json` | 1356 | `078cc253dc70fdc8a3b2ebe205a174740a60490cd02564ab73024938c2fcb207` |
| `headless-attempt-4/ui-desktop.png` | 381298 | `e3dd5e2c40dacd4bb2415bd22c0d419ece11b1e5bd6600e47b5ef7c606721ab2` |
| `headless-attempt-4/ui-mobile.png` | 354276 | `af66f28a4882624afda00bf862f8e37d1a5a109d2d5c2ee3efc1bdb5d5f1eb3b` |
| `evidence-manifest.json` | 11246 | `9fbf2910efa7129b29a7ea47599465441a8e226d8f5dfb194e85ab97776246ca` |
