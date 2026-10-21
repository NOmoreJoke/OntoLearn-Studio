# T10 私有准备验证

2026-10-21，独立 worktree；Node 24.15.0 / Python 3.12.12 / headless Chrome 155.0.8059.85。执行期间未启动 Electron、原生测试、HMR、凭据提示或指定审查应用。

| 验证 | 实际结果 |
| --- | --- |
| T10 pytest | 60 项通过；固定完整预期、角色/选项/版本/哈希、恶意 ZIP 布局及有界严格解压 |
| T10 vitest | 17 项通过；11 组恶意文本遍历所有动态文本位置、完整栏目/状态、逐 attempt 分类与访问器/预算 |
| 最终 `npm run check` | lint、格式、双端/单测类型、647 项 TS、构建、ruff、1,112 项 Python 全通过 |
| headless HTML | 11 个恶意字符串逐项与 DOM 文本完整相等；危险 DOM 节点 0，脚本哨兵未触发，外部请求空 |
| headless 组件 SSR | 4 个复选框全部未选、2 个按钮禁用、危险节点 0、无效投影产生 1 个 alert |
| 独立内审 | 两项 P2 及延伸路径实际修复、定向运行及完整私有范围复核通过，见 internal-review.md |

## 首次失败与证据

- `evidence/pytest-first.json` 按 UTF-8 原文及 SHA 保存：53/54 通过，NUL 名称反例构造被 ZipFile 写入器截断。原始 txt 的尾随空格保持在 JSON 字符串内，本地原件留在 out；改为篡改真实 ZIP 字节后检查正确拒绝。
- `evidence/check-first.txt` 原样保存：unit tsconfig 未配置 JSX，单测直接导入 TSX 导致 TS6142。未抢改共享配置；移除不必要静态 TSX 单测导入，组件另由实际 headless SSR 预验。
- 最终浏览器断言第一次使用 CLI VM 不支持的动态 import，错误原件留在本地 `evidence/out/browser-final-first-attempt.txt`。改为 CLI 外读取合成 fixture、以结构化进程参数传入字符串，再执行同一浏览器断言，最终通过；不是产品缺陷或生产验证。
- 完整原始日志及生成 HTML 留在本地忽略目录 `evidence/out/`；仓库保存紧凑摘要、关键浏览器 JSON、首失败原件与最终日志哈希，见 `verification-summary.json`。`render-probe.mjs` 可重建运行时 HTML。

## 未执行与门禁

没有改归档 PRD/source-manifest，未重新跑 sources；没有引入依赖/修改打包配置，未执行 unsigned 目录包或包内探针。独立组件未接入 App/bridge，普通桌面 e2e 不能替代本次浏览器预验，后续正式接线仍需隔离环境的真实 e2e/包内及双平台验证。

未取得正式导出投影/格式/checkpoint 与原子导入发布接口；未验收实际凭据排除、业务范围完整迁移、跨设备续编辑/查询/映射重跑冲突/撤销、真实逐 attempt 证据或沙盘重放。未进行指定 ZCode/MiniMax 双新审，未 push/PR/CI/合并。保留全部原父功能与完整发布门。
