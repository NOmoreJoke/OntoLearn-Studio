# 贡献与协作指南

欢迎参与 **OntoLearn Studio** 的开发与完善！本项目采用 **[Apache License 2.0](LICENSE)** 开源协议，所有向本仓库提交的贡献均默认按 Apache-2.0 协议授权。

## 1. 分支与提交规范

- **日常开发分支**：从 `develop` 拉取 `feat/<主题>`、`fix/<主题>`、`docs/<主题>` 或 `test/<主题>` 分支，以小范围 PR 合回 `develop`；里程碑版本再由 `develop` 合入 `main` 并打 Tag 发布。
- **历史不可改写**：禁止对共享分支（`main`、`develop`）执行 force-push 或重写已合入历史。
- **提交信息约定**：使用 Conventional Commits 前缀（`feat:`、`fix:`、`docs:`、`chore:`、`test:`、`refactor:`），并在 Commit Message 尾部附上本地实际执行通过的验证戳记，例如：
  ```text
  Verified: check,verify:sources
  ```

## 2. 提交前本地检查

在推送分支或发起 Pull Request 前，请在仓库根目录执行：

```bash
npm run verify:sources
node scripts/check-design-harness.mjs
npm run check
```

涉及桌面主进程、Preload 桥、引擎交互或渲染层端到端流程时，还须在构建后补充：

```bash
npm run test:e2e
```

若改动第三方依赖（`package.json`、`pyproject.toml` 或锁文件），须同步核验许可证与 Apache-2.0 的兼容性，并更新 `licenses/NOTICE` 及对应许可原文。

## 3. PR 内容与诚实边界

- **PR 描述要求**：在 `.github/pull_request_template.md` 中如实写明变更背景与结果、涉及模块/需求条款、本地与 CI 各自验证结果，以及已知限制。
- **禁止夸大能力**：未经真实运行与完整预期输出验证，不得在文档或界面中宣称支持完整无界 OWL DL、远程 SPARQL `SERVICE` 查询或黑盒自动决策；修改引擎语义行为必须补充固定完整预期输入输出测试。
- **严禁篡改冻结基线**：归档需求、初版原型及历史审查记录受 [`docs/source-manifest.json`](docs/source-manifest.json) 与 `scripts/verify-frozen-review-sources.mjs` 哈希锁定，默认不得改动或格式化，也不得为绕过校验覆盖旧哈希。
- **审查分级参考**：仓库变更分级规则详见 [`docs/process/review-policy.md`](docs/process/review-policy.md)，可使用 `npm run review:level` 预检当前分支的审查等级与机械完整性。
- **数据与凭据安全**：严禁提交真实密钥、`.env` 文件、个人/客户业务数据或本地运行数据库产物。
