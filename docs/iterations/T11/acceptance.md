# T11 独立工具验收与后续门

## 2026-10-23 F-1 新候选回归

唯一实现由 `verify.ts` 原字节重命名为 `verify.mts`，CLI直指真实扩展名；两专项通过 `.mjs` specifier的TS/Vite扩展替换引用同一 `.mts`，必须留 `tsc --listFiles` 的精确纳入证据。根package/锁/tsconfig/CI不变，不新增package或第二schema。原036及两份指定报告保持冻结；新候选另走完整指定双审。

CLI参数不足/过多、manifest与freeze分别缺失/格式错/16MiB超限、真实实现模块加载失败均须整段stderr严格固定、stdout空、exit2；禁止仅核最后一行。正常synthetic与CLI时钟回归须stderr空、原JSON/exit1语义不变。纯JS入口先拒绝Node24.0–24.2或非24.x（固定 `UNSUPPORTED_NODE_RUNTIME`），支持的Node24.3以上24.x才在try内加载 `.mts`。实际环境与模拟版本guard分开记录；不把version preload模拟当旧Node实机。独立warning preload须保留受控诊断，真实输入失败仍exit2，不能全局吞warning或以文档披露替代固定错误面。

## 原完整验收条件

原依据：PRD V0.6 第10–12节、附录C–G；外部本轮plan/requirements/acceptance、共同指令和T11启动提示。**状态唯一入口：`docs/iterations/W5/release-convergence-ledger.md`**（不再引用 `docs/reviews/T11/status.md`；`docs/reviews/T11/**` 为 T11 私有归档，本分支未引入，归档零新增）。

独立交付应具备：严格manifest v1；源/候选/受审/构建/报告SHA绑定；完整双目标与签名/公证/许可证/下载哈希一致性；T09固定案例manifest文件和G预期绑定；真实目标设备证据结构；恢复/迁移完整比较；冻结后指定模型/真人数据与辅助区分；错误路径拒绝。合成测试只验证核验器，不计其中任何真实发布验收。

验证命令：

```text
npx vitest run tests/unit/t11-release*.test.ts
T11_FIXED_BASELINE_PROBE=1 npx vitest run tests/unit/t11-release*.test.ts
npm run check
T11_FIXED_BASELINE_PROBE=1 npm run check
npm run verify:sources
npx prettier --check scripts/release/verify.mts scripts/release/verify-release.mjs tests/unit/t11-release*.test.ts tests/fixtures/release/*.json docs/release/*.md docs/iterations/T11/*.md
bash -n scripts/release/collect-macos.sh
git diff --check
```

**Wave 5 Stage 0 之后 `release/` 三重忽略盲区已修复**：`scripts/release/**` 与 `docs/release/**` 现已被正常 Git 追踪，并被标准 `npm run lint` / `npm run format:check` 覆盖。因此上述格式核验**不再需要** `--ignore-path /dev/null`，显式 lint 脚本也**不再需要** `npx eslint --no-ignore ...` 或 `--ignore-pattern '!scripts/release/**'`——那些写法是修复前的历史记录，保留仅为历史可追溯。修复后的根锚定规则为 `.gitignore` `/release/`、`.prettierignore` `/release`、`eslint.config.mjs` `'release/**'`。Windows collector因无批准Windows执行环境只静态审阅，不记运行通过。

固定输入联验需显式 `T11_FIXED_BASELINE_PROBE=1`。**Wave 5 Stage 1-A 已把它改为全时运行（0 skipped）、离线无 `.git` 可跑**：批准输入不再是历史提交 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的运行时 Git 对象，而是**仓内已提交的 18 文件基线** `tests/fixtures/product-baselines/manifest.json`（SHA-256 `0588f5804f0b13c55ccece009b444cfd3efcc572e53067703ca8d9224f4cf8ad`、`version: prd-v0.6-learning-1`、含 `content/learning/extensions.json`）与 PRD（SHA-256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`）。`scripts/release/verify.mts` 的 `APPROVED_BASELINE` 已直接硬钉该 manifest SHA 与 PRD SHA，并在核验时核对 PRD 中 **57 条 P0 `FR`** 抽取与 **`coverage.json` 50 条 G 用例**计数；任一不符即 `fail('PRD_SCOPE')`。因此默认 `npx vitest run tests/unit/t11-release*.test.ts` 已**全时执行、无 skipped**（本轮实测 `2 test files passed / 136 passed`，0 skipped），**不得再把「默认通过」与「显式探针联验」当成两件不同的事**。未来 CI 接线须确保批准的固定输入可取并显式执行，不能以 skip 关闭验收。

探针里的actual文件仍为由固定oracle构造的合成核验器输入，用于验证50条预期解析、RDF事实集合比较、E.5保序和拒绝行为；没有执行领域工具、模型或Store，不表示50项产品用例通过。

没有main/preload/bridge/CSP/window/engine依赖/打包配置变更，不在本机启动e2e/native/HMR，不重跑无关打包或产物。正式共享配置变更后按实际改动追加check、sources、目标隔离e2e/package及包内相同样例。此次不能把既有I04 CI当T11 CI。

后续完整T11关闭须：所有原P0和跨模块操作入口/G完整结果同候选通过；真实Win11/Mac15签名下载安装、凭据、恢复、双向迁移；既有合法API资源真实评估与零伪造；至少5真人/80%及迁移辅助反例；批准Q5口径与测量；同候选GLM-5.3/最高和M3.1-Flash/xhigh两个全新实际终态通过、全文读回及意见处理；门禁push/PR实际CI/正常合并远端核验；最终渠道实装验证。资源缺口只阻塞对应真实验收，独立实现与本地可恢复提交先推进。

2026-10-23修复候选按 [v3规范](selection-comparison-v3.md) 显式区分恢复/G.6并冻结case；生产批准profile固定**已提交的 18 文件唯一基线** `tests/fixtures/product-baselines/manifest.json`（SHA-256 `0588f5804f0b13c55ccece009b444cfd3efcc572e53067703ca8d9224f4cf8ad`、`version: prd-v0.6-learning-1`）与 PRD SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`；Q9路由、请求模型和批准来源双向pin；新增collector完成/同包声明及两项回退check。普通/大文件与CLI采用受控同fd读取，工程限额不作Q5性能门。IO专项用小文件和确定性模拟覆盖限额前拒绝、增长/短读/读异常关闭、非regular与叶替换、哈希和结构。Mac仅bash-n/静态；本轮不运行真实collector、目标设备、凭据、API或GUI。

## Wave 5 Stage 0 / Stage 1-A 追加验收（已落地，非计划）

| 追加项                                    | 证明单元                                                                                                                                                                                                                                                                                                                                                                         | 本轮实测                               |
| :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------- |
| `release/` 三重忽略盲区修复并内建标准门禁 | `git check-ignore -v scripts/release/verify.mts docs/release/README.md`（均 exit 1 = 未忽略）；`npx eslint --print-config scripts/release/verify.mts`（返回配置 = 未被忽略）；`npx eslint scripts/release --max-warnings 0`；`npx prettier --check scripts/release docs/release docs/iterations/T11`                                                                             | 全部 exit 0                            |
| 正式安装包目标与无签名目录预验分离        | `apps/desktop/electron-builder.yml`（mac `dmg`/arm64 + `hardenedRuntime` + `notarize`；win `nsis`/x64 + `signAndEditExecutable` + `signExecutable`；`forceCodeSigning: true`；零硬编码身份）；`apps/desktop/package.json` `package:dir` 显式覆写 `-c.forceCodeSigning=false -c.mac.identity=null -c.mac.hardenedRuntime=false -c.mac.notarize=false -c.win.signExecutable=false` | 静态核对通过；**未执行正式签名构建**   |
| 57 P0 + 50 附录 G 对账                    | `scripts/release/verify.mts`（`p0.length !== 57` → `fail('PRD_SCOPE')`；`coverage.json` 条目 `.length(50)`）                                                                                                                                                                                                                                                                     | 单测覆盖通过                           |
| 只读 T10 → `t11-comparison-v3` 投影       | `packages/engine/tests/test_w5_release_projection.py`                                                                                                                                                                                                                                                                                                                            | `6 passed`                             |
| 包内卫生门禁                              | `scripts/run-w5-packaged-release-hygiene.py`（6 项 `extraResources` 非空、零密钥/SQLite 残留、复检 Stage 0 打包不变量）                                                                                                                                                                                                                                                          | 已并入 CI 打包腿；本轮未产出正式包制品 |
| CLI 三态退出码                            | `scripts/release/verify-release.mjs`（参数/运行时/读取或格式错 → exit 2；`synthetic` 恒 exit 1；`evidence` 一致 → exit 0）                                                                                                                                                                                                                                                       | 单测覆盖通过                           |

投影脚本与卫生门禁**均不修改** `packages/engine/src/storage.py` 或 `transfer/service.py`，且输出恒定声明 `releaseAuthorized: false` 与 `installerAcceptanceClaimed: false`。本节任何一项都**不构成**发布许可，也**不闭合** `H1..H10` 中任一外部 HOLD。

两份全新指定模型审查须覆盖全部原工程及本次变更、18项原意见处置，不能复用已completed会话。本轮peer的prompt/receipt/report/state/metadata即使位于本方Git/索引也禁止读取；只读自己的receipt与显式列出的上一轮历史报告。owner事先核范围等价。独立agent内审不能替代此双审。
