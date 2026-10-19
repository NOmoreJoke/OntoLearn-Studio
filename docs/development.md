# 开发指南

## 工具与可重复安装

Node.js 24（`.node-version`）、Python 3.12（`.python-version`），npm workspace 管理 TypeScript，uv workspace 管理 Python。提交 `package-lock.json` 和 `uv.lock`，CI 使用 `npm ci` / `uv sync --frozen`。JS 直接依赖使用精确版本；Python 由锁文件固定传递依赖。根目录运行所有命令，含空格路径使用引号。

`npm run dev` 启动桌面端和仅绑定 127.0.0.1 的 Vite 开发服务；打包应用直接加载本地文件。引擎是受限 stdio 子进程，开发环境执行仓库 `.venv` 的 Python，打包环境执行随包提供的独立二进制，不依赖系统 Python。PyInstaller 产物必须在目标平台构建，不能用 macOS 产物直接发给 Windows。

## 常用命令

| 命令                     | 用途                                         |
| ------------------------ | -------------------------------------------- |
| `npm run dev`            | 启动真实桌面应用，包含 Vite 热更新           |
| `npm run check`          | 全部静态检查、单元测试和编译                 |
| `npm run test:e2e`       | 在已有编译产物上启动 Electron 并检查真实引擎 |
| `npm run verify:sources` | 校验已归档 PRD、原型及历史审查的字节一致性   |
| `npm run package:dir`    | 构建当前系统开发应用目录，内置引擎运行时     |
| `npm run format`         | 格式化开发文件；不会格式化归档源资料         |

## 故障处理

- 引擎未就绪：在仓库根目录重新执行 `uv sync --frozen`；当前只接受 Python 3.12。
- 开发端口被占用：关闭该仓库旧的开发进程后重启；服务固定 127.0.0.1:5173，禁止自动退让到外网接口。
- Linux 桌面测试：运行 `xvfb-run -a npm run test:e2e`，需系统具备 Electron 的 GUI 库。
- Electron 下载失败：恢复网络后执行 `npm ci`；不要通过关闭 TLS 校验处理。
- Windows：使用原生 Node、uv、Python；引擎路径自动选择 `.venv/Scripts/python.exe`。CI 会执行 Windows 编译和桌面冒烟，不等于正式首发支持承诺。
- 无法启动未签名打包应用：当前仅为开发验证产物；正式分发必须经过签名、公证和目标系统验证。

## 扩展边界

新增功能先更新需求追踪、类型/运行时校验和失败场景，再实现真实引擎。健康探针采用一次请求后退出的子进程；耗时业务接入前需设计持久进程、ExecutionJob 状态机、取消、崩溃恢复和资源上限。不得把当前探针直接扩展成任意 Python 命令执行接口。

新增模型 SDK 之前先实现最终外发授权和凭据存储。新增 SPARQL/RDF 依赖之前先完成附录 C/G 技术验证；仅设置配置项不能视为证明外联已被禁止。
