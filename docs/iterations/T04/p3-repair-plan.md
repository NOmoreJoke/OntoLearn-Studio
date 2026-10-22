# T04 四项 P3 最小修复计划

2026-10-23。总控明确接收旧产品 `554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6` 的同版完整 S1 双通过，并授权原 owner 在新独占树修复四项 P3。本计划先独立审技术选择，无阻断后实施。

## 身份与不变边界

- 新树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query-p3-repair`。
- 新分支：`feature/weekly-t04-query-p3-repair`；实际起点为固定 product 554，批准共享依赖/集成基线仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 旧开发树 `9da9da48b45b4f0cbbe084d95c3d23ebd85c579b`、两个 detached 9a review 树、原报告与输入均冻结。最新 AGENTS `de15f6ce…c8c4` 已原字节携带到新树，仅保护 M 未暂存。
- 不改 shared main/preload/contracts、reader、Store/worker/执行器、依赖/锁、其他 owner、验收真值。columns 空数组/ASK 等父元数据语义仍待批准；本次不借四 P3 改该接口。
- 无新 Goal、无模型 API/凭据/付款/账号重置、无 push/PR。新候选必要验证与独立审查后，指定双方必须重新完整同版审查，不沿用旧 Pass。

## 最小文件面与选择

| P3             | 实现文件                                             | 选择与理由                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 验证                                                                                                                                                                                          |
| -------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1 长度/trim   | `query_service/drafts.py`、renderer `query/draft.ts` | 只统一 draft 的 name/SPARQL：**原串先按 UTF-16 code units 限 128/65536，再去首尾空白，最后拒绝空串**。这匹配 TS/HTML 原始长度单位，比 Python 旧 code-point 上限更严格，不提高上限，也不把旧 Python 拒绝的超长空白串放行。两侧使用各自既有去空白集合的固定并集（Python 的 29 个空白字符 + ECMAScript 的 U+FEFF，共 30 个），避免 `.strip()`/`.trim()` 在 U+001C–1F、U+0085、U+FEFF 再分歧；中间字符保持不动，lone-surrogate/shape/scope/source 拒绝保留。description/question/RDF 序列化本次不改 | 两语言读取同一私有 boundary fixture：原始 128/129 与 65536/65537、首尾空白导致原串超限、64/65 emoji 的 UTF-16 边界、30 个边界空白、仅空白/内部空白/lone-surrogate；比较完整规范化值或明确拒绝 |
| D2 CSV 数值    | renderer `query/results.ts`                          | 列头须为 string；仅 string（包括列头）做现有公式/前导控制字符防护；有限 number / boolean 输出规范文本，null 保持空单元格。拒绝非有限 number 和非声明的运行时类型，不把对象/字符串误当数值；保留引号双写/CRLF/200 行边界                                                                                                                                                                                                                                                                         | 数值 -5/-0/小数/指数、bool/null 与字符串 `-5`/公式/前导空白/引号/逗号/换行的精确完整 CSV；非法 number/类型 fail-closed                                                                        |
| D3 16 字段 UX  | `QueryPage.tsx`                                      | 达 16 后只禁用未选字段；已选可取消，并显示“已选 n/16”。onChange 在最新 state 中防重复与超过上限，编译器 16 上限不变                                                                                                                                                                                                                                                                                                                                                                             | 真 DOM 选择 16→第17禁用→取消1项→可选第17，生成 SPARQL 核完整选择集合；已有 condition32 拒绝保留                                                                                               |
| D4 visual 重置 | `QueryPage.tsx`                                      | 新建、成功载入 saved query、成功载入 model draft 均清空 visual 的 class/fields/conditions；不从任意 SPARQL 猜反解，不改已有 definitionId/generation/保存身份逻辑。模板生成仍显式填自己的 visual。生成按钮在当前 visual 校验失败时禁用并给检查提示                                                                                                                                                                                                                                               | 真 DOM 对 A→载入B、A→新建、A→模型草稿分别核新文本/名称与 builder 清空；禁用生成不能把 A 静默覆盖回去，重新明确选择后才生成                                                                    |

专属测试/fixture：扩展 `tests/unit/t04-query-authoring.test.ts`、`tests/unit/t04-query-results.test.ts`、`packages/engine/tests/test_query_service_authoring.py`；新增 `tests/fixtures/query/draft-boundaries.json`、`tests/fixtures/query/p3-interaction.tsx` 与 `docs/iterations/T04/p3-interaction-probe.mjs`。既有 SSR 探针不计 interaction；仅若对应静态断言确需更新才修改，不机械增加镜像测试。另更新本方 T04 状态、设计/必要验证/审查证据。

## 真实交互方法与隔离

使用本树锁定的 Vite/React 与 `@playwright/test`。临时构建真实 QueryPage + 专属 synthetic catalog/saved/model fixture 为 IIFE，产物仅落 `test-results/t04-p3-repair/`；以 `page.setContent` / `addScriptTag` 加载到独立无端口页面，使用 Playwright 的真实 select/check/click/fill 和 DOM 断言，不直接调用 handler 或伪造 React state。独立 browser context 显式 offline，所有请求 route abort，记录任何请求尝试并拒绝意外外联。

锁定 Playwright 的目标 Chromium 1248 当前未安装；已只读确认 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` 存在。使用该已安装 Chrome 的 headless 独立实例（记录实际版本），TMP/profile/输出均指向本树 runtime，不打开或连接用户现有 profile/browser、不新增下载或依赖，不启动 Electron/App/HMR。产物是独立组件 fixture，未验证生产 CSP、App 路由/IPC/Store、下载/原生提示或父平台验收。需要实际有窗口互斥验收时另按总控资源交接，不把本探针升级为该证据。

## 执行与门禁

1. 独立 agent 只读审本计划和已有固定实现，先裁清技术选择；本轮只准备独立环境，不提前改产品。
2. 只在新树实施，先用专属断言及 interaction 定位四 P3；保首失败、完整 argv/cwd/起止/真实 exit/raw。禁止删断言、skip、筛绿或借加依赖绕过失败。
3. 实际实现变化按 AGENTS 跑完整 `npm run check`，另跑既有 SSR 与真实组件 interaction；依赖/归档/共享窗口面未改，不机械重跑 e2e/打包/verify:sources。出现实际对应风险再补检查。
4. 固定新候选，独立审完整 S1 与修复；反馈需改则重新验证真实受影响项。准备指定双方各全新完整同版任务，由总控交接短窗口，实际终态/全文报告/逐意见/CI/正常合并/远端门保持。
5. 父 query.execute/保存事务/查询元数据/T08/App/T10、两 OS/真人与全部原 P0 跨模块矩阵仍精确待验，不扩大为新宽方案或用四项修复关闭父功能。
