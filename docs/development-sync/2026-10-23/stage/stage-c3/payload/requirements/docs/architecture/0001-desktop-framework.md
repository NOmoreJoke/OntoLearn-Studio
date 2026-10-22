# ADR-0001：桌面开发框架与进程边界

日期：2026-10-19。状态：采用为开发骨架，待 M0 技术验证修订；不修改 PRD 未决产品事项。

## 背景与选择

PRD 要求本地安装、默认离线、六模块共用项目、确定性引擎与 Agent 解耦。当前没有应用代码和已确认技术栈。采用 npm + uv 单仓库：Electron 桌面壳、React/TypeScript 界面、Python 引擎、stdio 通信。Electron 的 TypeScript 主进程便于和前端共享边界类型，Python 保留本体生态的选型空间。

评估过 Tauri 2：包体较小，但引入 Rust 桥接层和 Python sidecar 的构建组合；当前选择 Electron 以减少开发语言数量。代价是较大应用体积、Chromium 安全更新维护成本。未测量安装包性能或对比体积，不宣称性能提升。桌面框架不替代首发操作系统、容量和本体能力决策。

## 当前实际实现

```text
React renderer（无 Node 能力）
  → preload: getEngineHealth()（唯一桥接方法）
  → 主进程：校验窗口、主 frame、来源 URL；合并并发健康请求
  → 固定可执行路径、无 shell 的 Python 子进程
  → 有版本的 JSON-lines health 请求（16 KiB 请求上限）
  → 运行时严格校验响应（64 KiB、5 秒上限）
  → 显示真实连接结果或可恢复错误
```

主进程启用 `contextIsolation`、`sandbox`，关闭 `nodeIntegration`、webview、窗口弹出、用户导航和权限请求。CSP 禁止外部脚本、iframe 与外部连接，开发态仅允许本地 HMR，并为 React Refresh 初始化脚本注入每次启动生成的 nonce。无远程字体、遥测、模型调用或 HTTP 引擎端口。preload 不暴露 ipcRenderer、通用 invoke、文件系统、shell 或渲染端指定路径。

Python 当前只实现健康探针，没有查询、推理、映射、保存、Agent、数据库或沙盘实现。无本体引擎依赖，是刻意保留 M0 能力验证门槛；候选 RDFLib/pySHACL/受控规则需用代表样例验证后另立 ADR。

## 后续领域层次（尚未实现）

- 桌面基础设施：文件选择、项目生命周期、凭据安全存储、限权工具调度。
- 应用层：版本化 Command/ChangeSet、ExecutionJob、授权检查、结果失效。
- 领域层：本体、断言图、推导图、隔离场景、不可变历史运行。
- 引擎适配器：RDF/只读查询、SHACL、推理、行为与固定轮次执行。
- 存储适配器：拟使用 SQLite 事务保存清单和元数据，图存储待验证；未冻结文件格式和迁移策略。
- Agent 适配器：只生成草稿和调用授权工具，不参与确定性引擎结论判定。

正式写入前必须验证 PRD 的原子提交、旧 ChangeSet 冲突、推导撤回、历史不可变与依赖失效。不要先引入云数据库、HTTP API、复杂多 Agent 或未经测量的图数据库部署。

## 构建与发布边界

PyInstaller onedir 将引擎连同 Python 运行时放入应用 resources，Electron Builder 打包当前平台应用目录。当前只输出未签名开发目录；正式签名、公证、安装器、升级和跨设备恢复属于后续工作。CI 的跨系统构建只验证开发兼容性，不代替目标系统安装验收。

参考依据：[Electron 安全](https://www.electronjs.org/docs/latest/tutorial/security)、[上下文隔离](https://www.electronjs.org/docs/latest/tutorial/context-isolation)、[electron-vite](https://electron-vite.org/guide/)、[PyInstaller 平台构建边界](https://pyinstaller.org/en/stable/operating-mode.html)、[Tauri 项目配置](https://v2.tauri.app/start/frontend/)。

依赖维护：electron-builder 的代理下载依赖链原含 sprintf-js 已知拒绝服务问题；固定 global-agent 4.1.3 移除该旧链。此约束需随 builder 升级评估移除，并验证下载与打包。
