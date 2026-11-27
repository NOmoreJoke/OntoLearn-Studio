# 安全策略（Security Policy）

## 支持版本

| 版本    | 安全维护状态           |
| :------ | :--------------------- |
| `0.1.x` | 活跃维护（社区预览版） |

## 私密漏洞披露

如果您在 **OntoLearn Studio** 中发现了安全漏洞，**请勿通过公开 Issue、PR 或社区讨论区披露可利用细节、凭据或真实业务数据**。

请优先通过 GitHub 仓库的 **Security → Advisories → Report a vulnerability** 提交私密安全报告，建议在报告中附带：

- 漏洞影响模块与版本（或 Commit SHA）；
- 最小可复现步骤（请使用脱敏示例数据）；
- 潜在安全影响评估与修复建议（如有）。

## 现行安全架构与隔离边界

OntoLearn Studio 按 **本地优先、默认零外发、最小权限** 原则设计以下安全防线：

1. **渲染层沙箱与受限 Preload 桥**：
   - 渲染窗口强制启用 `contextIsolation: true`、`sandbox: true`，关闭 `nodeIntegration`、`webviewTag` 与任意外部导航/弹窗。
   - Preload 仅暴露业务命名的受限 API，禁止暴露 `ipcRenderer`、通用 `invoke`、任意文件系统路径或 shell 执行能力；主进程校验发送窗口、主 frame、来源 URL 及 Zod Schema 边界。
2. **双态严格 CSP（Content Security Policy）**：
   - 生产与开发双态均禁止 `unsafe-inline` 与 `unsafe-eval` 脚本执行，阻断外部脚本、iframe 与未授权外联；开发态仅放行绑定 `127.0.0.1` 的本地 Vite HMR 且使用启动级随机 nonce。
3. **本地语义引擎与输入/输出防线**：
   - Python 3.12 常驻协调器通过无 shell stdio JSONL 通信并持有 SQLite Writer Lease，支持 `ExecutionJob` 超时、取消与崩溃恢复。
   - 本地 SPARQL 查询强制只读执行，禁用 `SERVICE` 联邦外联及 SPARQL Update 写操作。
   - CSV 与 Excel (`.xlsx`) 导入集成 `defusedxml` 解析防护及大小/边界限制；导出的自包含 HTML 报告执行上下文转义且禁止外部网络资源加载。
4. **可选模型网关外发控制**：
   - 模型 API Key 通过操作系统 `safeStorage` 加密存储，禁止明文落盘。
   - 任何外发调用默认关闭，调用前须经过本地脱敏预览与人工逐次确认，且模型输出仅作待审核草稿。
5. **供应链与发布完整性**：
   - 前后端依赖由 `package-lock.json` 与 `uv.lock` 严格锁定；GitHub Actions 全部第三方 Action 固定至完整 Commit SHA，PR CI 默认只读权限且不使用真实签名凭据。
   - 正式与社区构建均通过 `npm run release:hygiene` 检查无密钥残留并生成 `SHA256SUMS.txt` 校验和。
