# 审查清单使用说明（核心 20 / 领域模块 / 原始 160 条）

分级审查（L0/L1/L2）于 2026-10-29 经用户正式采纳，从 T04 起执行，T02 保留原门禁。当前政策与 `verify-candidate` CI 均为**报告模式（`adopted_report_only`）**：自动 gate（required check、标签、自动阻断）尚未启用，启用前工程接线仍按已生效的指定双审/完整验收执行。分级规则正文见 [AGENTS.md](../../AGENTS.md) 第 5 节与 [.github/review-policy.yml](../../.github/review-policy.yml)。

**首次可信基线的过渡边界**：新 gate 尚无可信基线时，report job 的 bootstrap/unknown 状态不可当作新 gate 终态 Pass；本工程交付在旧门禁（指定双审＋完整 CI＋手工可信身份核验）下审查通过后，才形成新 gate 的可信基线，再验证与启用。不为让首个 bootstrap 报告变 Pass 而自信任候选代码。

## 本目录文件

| 文件                                 | 作用                                                                            |
| ------------------------------------ | ------------------------------------------------------------------------------- |
| `core-20.md`                         | 每次 L1/L2 都必须覆盖的核心 20 项检查与 L2 A/B 分工                             |
| `domain-modules.md`                  | 按路径与语义加载的领域模块（security/storage/contracts/engine/agent/packaging） |
| `source-checklist-index.json`        | 原始 160 条清单的逐条索引：原文、顺序、逐条 sha256、核心/领域路由建议           |
| `user-review-checklist-20261024.txt` | 原始清单的字节精确仓内副本（完整性锚点，不得修改）                              |

## 作用边界

- 路由只是确定**读什么**，不表示检查已通过，也不扩大当前产品范围。每次 L1/L2 先对每条判适用性：**适用 / 不适用（写理由）/ 无法确认（写缺什么）**。
- 原清单共 160 个引用条目 = **147 条产品/工程检查 + 13 条人员职责附录**。角色附录（S148–S160）是人员责任语境，不是产品验收项；不能把角色要求当成新增产品功能，也不能默默删去任何条目。
- 原清单中的 SaaS 登录、计费、SOC2/HIPAA 等条目，须先对实际本地桌面产品和本 PR 判适用性；产品不存在的能力不为凑清单新增。独立发布、隐私、法律类 HOLD 仍保留，不在局部 PR 中虚报解决。

## 完整性锚点与机器校验

- 原文清单全文 SHA-256 锚点：`1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`（同时记录于 `source-checklist-index.json` 的 `sourceSha256` 与 `scripts/lib/checklist.mjs` 的 `ANCHOR_SOURCE_SHA256`）。
- `scripts/verify-candidate.mjs` 每次运行都会校验：仓内原文副本与锚点一致、索引 `sourceSha256` 与副本一致、160 条逐条 sha256 与记录一致、序号 1..160 连续、147+13 计数正确。任何原文/条目改动、增删条目都会判 `fail`；校验器不做任何"恢复原文造相等"。
- 适配说明：仓内索引仅将 `sourcePath` 从外部绝对路径改为仓内相对路径并添加 `provenance` 溯源块；`items` 数组逐字节保留，外部原件 hash 见 `provenance.externalIndexSha256`。

## 审查使用流程

1. 运行 `node scripts/verify-candidate.mjs --base <sha> --head <sha> ...` 获取机械身份与分级 JSON（C02 的共用输入）。
2. 按分级等级加载 [core-20.md](./core-20.md)；L1 指定审查员覆盖全部 20 项及适用模块，L2 按 A/B 主责分工。
3. 按 diff 路径与语义在 [domain-modules.md](./domain-modules.md) 选择领域模块；无法判定的按 needs_triage 流程走可信人工决策（决策文件须绑定政策版本与候选 head）。
4. 需要回溯原始条目原文时查 [source-checklist-index.json](./source-checklist-index.json)（含每条的 `coreRoutes`/`domainRoutes` 路由建议，路由建议本身不构成检查结论）。
5. 报告模板：记录候选身份（引用机械结果）、等级、模型/分工、范围、适用模块；给出 Pass / ConditionalPass / Fail；逐项列发现 ID、严重性、位置、风险、反例与处置要求；标注未检查/无法确认处。没有发现也须说明实际覆盖范围，不能把未查内容写成通过。
