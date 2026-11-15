# OntoLearn Studio 开发规则

- 默认中文，结论先行。先读取当前 PRD 的对应条款与附录 C/D/E/G，再修改业务语义。
- 当前是 M0 开发骨架；除健康探针外，业务模块尚未实现。禁止将占位界面描述成已经实现的能力。
- 本地优先；不自动启用模型、遥测或云服务。渲染端不得直接使用 Node、文件系统、shell 或通用 IPC。
- 领域引擎与 Agent 解耦；确定性结果必须来自真实引擎，修改须版本化、可预览、原子提交。
- 保留本体定义、断言事实、当前推导、场景副本与历史运行的层次边界。
- 不提交凭据、业务数据和运行数据库；归档 PRD、审查、.pen 不批量格式化。
- 使用 npm workspace 和 uv workspace，提交两种锁文件。运行 `npm run check` 与 `npm run verify:sources`；桌面或桥接改动运行 `npm run test:e2e`。
- 复杂或高风险交付使用独立 agent 审查，避免共享文件争写。验收结果明确区分静态、运行、打包和生产证据。
- 审查按 [审查分级政策](docs/process/review-policy.md) 执行：L0 自动 / L1 单审 / L2 双审，用 `npm run review:level` 计算等级；先 CI 后审查，补丁未变的 rebase 不复审，复审最多 2 轮。
