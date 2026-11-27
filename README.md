# OntoLearn Studio

**OntoLearn Studio** 是一款**本地优先（Local-First）、零外发默认安全的本体建模学习与落地桌面工作台**，内置独立打包的 Python 语义引擎（RDFLib + pySHACL + owlrl）与 SQLite 单事务真值存储，面向零代码业务/产品人员与本体工程师提供可交互、可回滚、可解释的全链路实操环境。

> 许可证：[Apache-2.0](LICENSE) · 第三方依赖许可清单见 [licenses/NOTICE](licenses/NOTICE)

---

## 核心能力（`00` – `08` 一体化工作台）

- **零代码底层概念预热（`00 三元组与概念沙盒`）**：
  - 提供 **Lv.1 知味茶饮（全渠道会员与门店订单履约）** 6 步闯关沙盒：从 Excel 表格行拆解 `主语 — 谓语 → 宾语` 三元组、同名“王敏”身份消歧（IRI vs Label）、事件实体化（`#SO-101` 多杯订单）、到 PRD 四色圈词与实时双形状 SVG 图谱。
- **零代码与标准 RDF 双视图建模（`01 本体构建`）**：
  - 支持 `[零代码业务导引 | 标准 RDF/IRI 视图]` 一键切换与自然语言下拉造句，所有写操作均先预览事务 Diff（`ReadableBusinessDiff` 三列表 + 可展开的 JSON/RDF 原文抽屉）并人工确认后原子提交。
- **全流程工程工作台（`02` – `08`）**：
  - `02 数据映射`：CSV / Excel (`.xlsx`) 映射、稳定个体身份校验与快照可追溯导入；
  - `03 本体查询`：SPARQL 与可视化查询构造，支持有界分页、历史快照重跑与 CSV 导出；
  - `04 质量与推导`：SHACL 结构校验、单阶段规则与 RDFS 继承推导，内置 **知味茶饮 10 行微缩集 & 80 行脏数据压力仿真** 与白话推导证据链；
  - `05 行为定义` & `06 情景推演`：事件触发规则沙盘与多轮指标推演；
  - `07 独立迁移练习` & `08 导出与迁移`：整项目 `.zip` 导入导出、检查点整库恢复与含版本/过期标识的 HTML 报告导出；
  - **受控离线导师与可选模型助手**：零模型 API 即可离线完成全部分阶教学与提示检查；配置模型 Key 后仅生成供人工核对的 Diff 草稿，不绕过确认直接落库。

---

## 桌面端安装使用（最终用户无需安装 Python / Node）

桌面安装包已完整内置冻结的 Python 语义引擎与运行时依赖。

| 平台        | 目标架构                       | 安装包格式                             | 社区免证书签名构建首次启动说明                                                                                                         |
| :---------- | :----------------------------- | :------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| **macOS**   | Apple Silicon (`arm64`, M1–M4) | `OntoLearn Studio-<version>-arm64.dmg` | 打开 DMG 拖入「应用程序」；若提示「无法验证开发者」，在终端执行一次：<br>`xattr -cr "/Applications/OntoLearn Studio.app"` 即可正常打开 |
| **Windows** | Windows 10 / 11 (`x64`)        | `OntoLearn Studio Setup <version>.exe` | 安装向导支持自定义安装目录（如 `D:\OntoLearn Studio`）；若弹出 Windows SmartScreen 蓝色提示，点击 **「更多信息 → 仍要运行」** 即可     |

> 注：仓库配置保留完整正式发布代码签名与公证支持（在 GitHub Actions Secrets 注入 Apple `CSC_LINK` / 公证凭据或 Windows `WIN_CSC_LINK` 时自动生成签名与公证包；未注入凭据时构建带 `SHA256SUMS.txt` 校验和的社区无签名安装包）。

---

## 源码开发与本地构建

开发环境依赖 **Node.js 24**、**Python 3.12** 与 **[uv](https://docs.astral.sh/uv/getting-started/installation/)**。

```bash
git clone https://github.com/NOmoreJoke/OntoLearn-Studio.git
cd OntoLearn-Studio
git switch develop
npm ci
uv sync --frozen
npm run dev
```

### 常用验证与打包命令

```bash
npm run check            # ESLint + Prettier + TypeScript + Vitest + 构建 + Ruff + Pytest
npm run verify:sources   # 归档源文件 SHA-256 核对
npm run test:e2e         # 真实 Electron Playwright E2E（Linux 需 xvfb-run -a）
npm run package:dir      # 生成当前系统无签名应用目录包（含冻结 Python 引擎）
npm run release:hygiene  # 对 release/ 执行 6 项 extraResources 与零密钥残留卫生检查
```

按标签触发双平台安装包发布（自动在 `macos-latest` 与 `windows-latest` 构建并发布到 GitHub Releases）：

```bash
git tag v0.1.0
git push origin v0.1.0
```

---

## 目录结构

```text
apps/desktop/         Electron 主进程、受限 preload、React 渲染端、图标与打包配置
packages/contracts/   TypeScript / Python 共享契约定义与运行时校验
packages/engine/      Python stdio 语义引擎、SQLite 事务存储、PyInstaller 入口与单测
content/learning/     离线课程、双案例教学资源与术语表
licenses/             第三方开源组件原始许可证与 NOTICE 汇总
scripts/              引擎打包、设计门禁、发布卫生核验与 CI 编排脚本
tests/                TS 单元测试、属性测试与 Electron E2E 用例
docs/                 需求基线（PRD）、架构决策、迭代规格与发布核验文档
.github/workflows/    三平台 PR CI（ci.yml）与双平台安装包发布流水线（release.yml）
```

## 开源协议与安全反馈

本项目采用 [Apache License 2.0](LICENSE) 开源发布。欢迎通过 Issue / Pull Request 参与贡献（见 [CONTRIBUTING.md](CONTRIBUTING.md)），安全漏洞披露请参考 [SECURITY.md](SECURITY.md)。
