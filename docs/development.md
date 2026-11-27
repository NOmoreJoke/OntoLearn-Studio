# 开发指南

## 工具与可重复安装

开发环境使用 Node.js 24（[`.node-version`](../.node-version)）与 Python 3.12（[`.python-version`](../.python-version)），分别由 npm workspace 与 `uv` workspace 管理。`package-lock.json` 与 `uv.lock` 必须随依赖变更同步提交，CI 严格使用 `npm ci` 与 `uv sync --frozen`。请在仓库根目录运行所有命令；路径含空格时注意加引号。

`npm run dev` 启动桌面端与仅绑定 `127.0.0.1` 的 Vite 开发服务；打包应用直接加载本地构建产物。语义引擎运行于受监管的无 shell stdio 常驻协调器进程：开发态执行 `.venv` 中的 Python 3.12，打包态执行随 `resources/engine/` 分发的 PyInstaller 独立二进制，不依赖用户系统 Python。PyInstaller 产物必须在目标操作系统原生构建（macOS 与 Windows 产物互不通用）。

## 常用命令

| 命令                                    | 用途                                                                           |
| :-------------------------------------- | :----------------------------------------------------------------------------- |
| `npm run dev`                           | 启动真实桌面应用（含 Vite 本地热更新）                                         |
| `npm run check`                         | 运行全部静态检查（ESLint、Prettier、tsc）、Vitest、构建、Ruff 与 Pytest        |
| `npm run test:e2e`                      | 在已有构建产物上启动真实 Electron 运行 Playwright E2E                          |
| `npm run verify:sources`                | 校验 [`source-manifest.json`](source-manifest.json) 锁定的归档源资料字节一致性 |
| `node scripts/check-design-harness.mjs` | 校验渲染层语义 Token 与 Design Harness 确定性规则                              |
| `npm run review:level`                  | 计算当前分支相对 `origin/develop` 的代码审查等级（`L0`/`L1`/`L2`）             |
| `npm run package:dir`                   | 构建当前系统应用目录包（内置 PyInstaller 冻结引擎运行时）                      |
| `npm run release:hygiene`               | 校验 `release/` 产物的 extraResources、第三方许可与零密钥残留                  |
| `npm run format`                        | 格式化开发源码与文档（自动跳过受保护的归档源资料）                             |

## 故障处理

- **引擎未就绪**：在仓库根目录重新执行 `uv sync --frozen`；项目当前仅接受 Python 3.12。
- **开发端口被占用**：关闭残留开发进程后重启；开发服务固定监听 `127.0.0.1:5173`，禁止自动暴露到局域网或外网接口。
- **Linux 桌面测试**：执行 `xvfb-run -a npm run test:e2e`，需系统安装 Electron 所需的 GUI 依赖库。
- **Electron 下载失败**：恢复网络后重跑 `npm ci`，禁止通过关闭 TLS 校验绕过网络问题。
- **Windows 环境**：使用原生 Node.js、`uv` 与 Python；引擎路径自动定位 `.venv/Scripts/python.exe`。
- **社区无签名包首次启动**：未注入 Apple 公证或 Windows 代码签名 Secrets 时，`package:dir` 与 Release 工作流默认生成社区无签名包；正式商用签名与目标真机验收须按外部证书与 [`verification/VERIFY.md`](verification/VERIFY.md) 流程执行。

## 架构与扩展边界

- **常驻引擎与任务状态机**：主进程通过 `EngineSupervisor` 管理常驻协调器与 `ExecutionJob` 生命周期，配合 SQLite Writer Lease 与事务恢复机制确保窗口崩溃或重启后不丢失已提交状态、不自动重放未确认写任务（详见 [`architecture/0003-resident-coordinator-and-jobs.md`](architecture/0003-resident-coordinator-and-jobs.md)）。
- **IPC 与安全约束**：Preload 仅暴露业务命名的受限接口，禁止直接暴露 `ipcRenderer`、任意文件路径或命令行执行入口；渲染层严格遵循双态零 `unsafe-inline` / `unsafe-eval` CSP。
- **模型外发与数据安全**：外部模型调用默认关闭，新增或调整模型网关逻辑必须保持凭据 `safeStorage` 加密、脱敏负载预览与逐次人工确认边界，详见 [`../SECURITY.md`](../SECURITY.md) 与 [`../CONTRIBUTING.md`](../CONTRIBUTING.md)。
- **审查与验证纪律**：所有变更按 [`process/review-policy.md`](process/review-policy.md) 分级，改动核心引擎/契约/主进程须经过双审（`L2`）与对应 Diff 触发验证。
