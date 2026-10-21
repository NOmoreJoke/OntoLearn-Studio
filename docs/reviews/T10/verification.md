# T10 私有准备验证

2026-10-21，独立 worktree；Node 24.15.0 / Python 3.12.12 / headless Chrome 155.0.8059.85。执行期间未启动 Electron、原生测试、HMR、凭据提示或指定审查应用。

| 验证                 | 实际结果                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| T10 pytest           | 60 项通过；固定完整预期、角色/选项/版本/哈希、恶意 ZIP 布局及有界严格解压                                                |
| T10 vitest           | 报告 18 项、文件发布 43 项通过；12 组恶意文本、完整栏目/状态、逐 attempt 分类、访问器/预算及真实 FS                      |
| 最终 `npm run check` | lint、格式、双端/单测类型、691 项 TS、构建、ruff、1,112 项 Python 全通过，直接命令进程 exit 0                            |
| headless HTML        | 打开真实文件服务发布的产物；12 个恶意字符串及前导 LF 与 DOM 文本完整相等，危险节点 0，脚本哨兵未触发，外部请求空         |
| headless 组件 SSR    | 4 个复选框全部未选、2 个按钮禁用、危险节点 0、无效投影产生 1 个 alert                                                    |
| 独立内审             | 新增文件服务 3 项 P2 及清理并发建议实际修复，完整私有候选复核通过，见 report-file-internal-review.md；旧内审作为历史保留 |

## 首次失败与证据

- `evidence/pytest-first.json` 按 UTF-8 原文及 SHA 保存：53/54 通过，NUL 名称反例构造被 ZipFile 写入器截断。原始 txt 的尾随空格保持在 JSON 字符串内，本地原件留在 out；改为篡改真实 ZIP 字节后检查正确拒绝。
- `evidence/check-first.txt` 原样保存：unit tsconfig 未配置 JSX，单测直接导入 TSX 导致 TS6142。未抢改共享配置；移除不必要静态 TSX 单测导入，组件另由实际 headless SSR 预验。
- 最终浏览器断言第一次使用 CLI VM 不支持的动态 import，错误原件留在本地 `evidence/out/browser-final-first-attempt.txt`。改为 CLI 外读取合成 fixture、以结构化进程参数传入字符串，再执行同一浏览器断言，最终通过；不是产品缺陷或生产验证。
- 完整原始日志及生成 HTML 留在本地忽略目录 `evidence/out/`；仓库保存紧凑摘要、关键浏览器 JSON、首失败原件与最终日志哈希，见 `verification-summary.json`。`render-probe.mjs` 可重建运行时 HTML。
- 新增文件服务首 check 在控制字符 regex 上触发 ESLint；已改逐字符检查。目录 fsync 注入初版未匹配 macOS realpath，原测试和全 check 均如实失败，改用 canonical parent 并断言注入一次后通过。原件按 UTF-8/SHA 保存在 report-file-failures.json，本地原始 txt 未改写。
- 文件服务故障测试默认执行真实 Node fs；只有命名路径包装实际 link 的响应和一个真实目录句柄 sync。权限不可读测试在 macOS 临时目录执行 chmod 后读回，Windows 此类用例明确跳过，不作双平台证明。

## 未执行与门禁

没有改归档 PRD/source-manifest，未重新跑 sources；没有引入依赖/修改打包配置，未执行 unsigned 目录包或包内探针。新增私有 main 服务触发的 e2e 要求保留，当前服务和组件未接入 App/bridge；普通旧桌面 e2e 不覆盖该能力，后续正式接线需隔离环境的真实 e2e/native picker/包内及双平台验证，本机未启动 Electron。

未取得正式导出投影/格式/checkpoint 与原子导入发布接口；未验收实际凭据排除、业务范围完整迁移、跨设备续编辑/查询/映射重跑冲突/撤销、真实逐 attempt 证据或沙盘重放。未进行指定 ZCode/MiniMax 双新审，未 push/PR/CI/合并。保留全部原父功能与完整发布门。
