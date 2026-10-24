# OntoLearn Studio

本地优先的本体学习与落地 Agent 工作台。从业务概念、数据映射到查询、推理、行为与沙盘，在同一项目中学习与验证。

**当前状态：M0 开发骨架。** PRD V0.6 与可编辑原型已归档；桌面端可检查真实 Python 引擎连接。六模块业务、项目保存和模型调用尚未实现，本次交付不代表完成 M0 或发布 MVP。

## 快速开始

开发者需要 Node.js 24、Python 3.12 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)。最终用户运行环境将随安装包提供，开发依赖要求不等于最终安装要求。

```bash
git clone https://github.com/NOmoreJoke/OntoLearn-Studio.git
cd OntoLearn-Studio
git switch develop
npm ci
uv sync --frozen
npm run dev
```

点击“检查本地引擎”，验证 Electron → preload → 主进程 → Python stdio → 协议校验的连接。不需要 API key，不启动 HTTP 服务，不请求外部模型。

```bash
npm run check            # lint、格式、类型、TS/Python 测试与构建
npm run verify:sources   # 归档资料 SHA-256 核对
npm run test:e2e         # 构建后运行真实 Electron 冒烟；Linux 使用 xvfb-run -a
npm run package:dir      # 打包当前系统的应用目录，包含独立 Python 引擎
```

打包输出位于 `release/`；当前仅提供未签名开发产物，不生成发布版安装器、不上传 Release。签名、公证、自动更新、离线课程和业务引擎需后续里程碑实现。

## 目录

```text
apps/desktop/         Electron 主进程、受限 preload、React 渲染端
packages/contracts/  TS 边界类型与运行时校验
packages/engine/     Python stdio 引擎、协议与测试
scripts/             引擎打包、资料校验
tests/               TS 单元测试与桌面冒烟
design/prototypes/   原样归档的 .pen 原型
docs/prd/            PRD V0.6
docs/reviews/        需求与原型历次审查
docs/architecture/   技术边界与架构决策
.github/             CI、依赖更新、问题与 PR 模板
```

## 开发约定

- `main`：已提交的资料基线与经 PR 审核后的稳定代码。
- `develop`：集成开发分支；新工作从这里创建 `feat/<主题>` 或 `fix/<主题>`。
- 功能 PR 合入 `develop`；阶段交付通过 PR 从 `develop` 合入 `main`。不使用强制推送覆盖共享历史。
- 未实施分支保护规则，当前依靠 PR 工作约定；有协作者后可在 GitHub 配置强制检查和评审。

更多内容见 [资料索引](docs/README.md)、[开发指南](docs/development.md)、[架构决策](docs/architecture/0001-desktop-framework.md)、[M0 清单](docs/m0-checklist.md) 与 [贡献说明](CONTRIBUTING.md)。仓库保持私有，未擅自指定开源许可证。
