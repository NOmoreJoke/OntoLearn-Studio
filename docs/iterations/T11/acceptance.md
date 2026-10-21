# T11 独立工具验收与后续门

原依据：PRD V0.6 第10–12节、附录C–G；外部本轮plan/requirements/acceptance、共同指令和T11启动提示。状态唯一入口：`docs/reviews/T11/status.md`。

独立交付应具备：严格manifest v1；源/候选/受审/构建/报告SHA绑定；完整双目标与签名/公证/许可证/下载哈希一致性；T09固定案例manifest文件和G预期绑定；真实目标设备证据结构；恢复/迁移完整比较；冻结后指定模型/真人数据与辅助区分；错误路径拒绝。合成测试只验证核验器，不计其中任何真实发布验收。

验证命令：

```text
npx vitest run tests/unit/t11-release.test.ts
npm run check
npm run verify:sources
npx prettier --ignore-path /dev/null --check scripts/release/verify.ts scripts/release/verify-release.mjs tests/unit/t11-release.test.ts tests/fixtures/release/*.json docs/release/*.md docs/iterations/T11/*.md
bash -n scripts/release/collect-macos.sh
git diff --check
```

路径名 `release` 被现有 eslint/prettier 全局忽略，必须显式 `--ignore-path /dev/null` 格式核验且对TS通过测试引用纳入typecheck。显式lint脚本另用 `npx eslint --no-ignore scripts/release/verify.ts scripts/release/verify-release.mjs`；若忽略规则无法覆盖则使用配置的 `--ignore-pattern '!scripts/release/**'` 并核验确实进入文件。Windows collector因无批准Windows执行环境只静态审阅，不记运行通过。

没有main/preload/bridge/CSP/window/engine依赖/打包配置变更，不在本机启动e2e/native/HMR，不重跑无关打包或产物。正式共享配置变更后按实际改动追加check、sources、目标隔离e2e/package及包内相同样例。此次不能把既有I04 CI当T11 CI。

后续完整T11关闭须：所有原P0和跨模块操作入口/G完整结果同候选通过；真实Win11/Mac15签名下载安装、凭据、恢复、双向迁移；既有合法API资源真实评估与零伪造；至少5真人/80%及迁移辅助反例；批准Q5口径与测量；同候选GLM-5.3/最高和M3.1-Flash/xhigh两个全新实际终态通过、全文读回及意见处理；门禁push/PR实际CI/正常合并远端核验；最终渠道实装验证。资源缺口只阻塞对应真实验收，独立实现与本地可恢复提交先推进。
