# 更新日志（Changelog）

本文件按 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范记录 **OntoLearn Studio** 的主要版本演进。

## [0.1.0] - 2026-11-27

首个公开开源版本，完整交付零代码本体概念预热、全链路语义工程工作台、双平台桌面安装包与自动化发布流水线。

### 新增（Added）

- **零代码概念沙盒与双案例仿真体系（Wave 7）**：
  - 新增 `00 三元组与概念沙盒`：提供 6 步零代码闯关交互与 PRD 四色圈词 / 坏模型重构诊所。
  - 新增 `Lv.1 知味茶饮 · 全渠道会员与门店订单履约` 仿真课程与 `10 行微缩集 / 80 行含脏数据压力集` 一键切换，完整保留 `Lv.2 智能工厂` 工程迁移案例。
  - `01 本体构建` 新增 `[零代码业务视图 | 标准 RDF/IRI 视图]` 切换、自然语言下拉造句器与三列可读变更预览（`ReadableBusinessDiff`）。
- **Design Harness 与双模 UI 壳层（Wave 6）**：
  - 升级 V2 原型与四层 `design-harness/` 设计底座，引入确定性设计门禁脚本（`scripts/check-design-harness.mjs`）。
  - 统一左侧工作台导航与右侧 `[课程导师 | AI 助手]` 边栏及顶栏快照/检查点抽屉。
- **全链路本体工程工作台（Waves 1–5）**：
  - 落地 `01 本体构建`、`02 数据映射`（CSV / XLSX）、`03 本体查询`（本地只读 SPARQL 与可视化构造、历史快照重跑）、`04 质量与推导`（SHACL 与单阶段规则/OWL-RL 子集推导）、`05 行为定义`、`06 情景推演`、`07 迁移练习`、`08 导出与迁移`（`.zip` 整包迁移、检查点整库恢复、离线 HTML 报告）。
  - 落地 `B1a/B1b` 项目生命周期与快照失效追踪、`L1/Lq` 离线学习账本与课程验收闭环、`I06` 可选模型网关（`safeStorage` 加密凭据 + 脱敏外发预览 + 人工确认）。
- **底层安全架构与常驻语义引擎（I01–I04）**：
  - 常驻受监管 Python 3.12 协调器（`RDFLib` + `pySHACL` + `owlrl` + SQLite 单库原子事务与 Writer Lease），支持 `ExecutionJob` 取消与主进程崩溃/无响应恢复。
  - 启用 `contextIsolation`、`sandbox`、方法级白名单 Preload 桥与开发/生产双态严格 CSP（零 `unsafe-inline` / `unsafe-eval`）。
- **开源协议与双平台桌面发布（Wave 8）**：
  - 采用 **Apache License 2.0** 开源，补全 `licenses/NOTICE` 与第三方依赖原始许可文本。
  - 补全 macOS（`icon.icns`）、Windows（`icon.ico`）与 Linux（`icon.png`）应用图标，配置 NSIS 自定义安装目录与 GitHub Releases 双平台（`macOS arm64 .dmg` + `Windows x64 .exe` + `SHA256SUMS.txt`）自动构建工作流。
