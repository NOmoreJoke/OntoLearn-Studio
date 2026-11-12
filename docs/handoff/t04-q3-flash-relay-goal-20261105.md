# T04 Q3 同快照图 · Flash 接力 Goal（2026-11-05）

**授权**：Kaiming 选定「开 T04 Q3：GLM Flash 写 → MiniMax Flash 审」。  
**基线**：`origin/develop` @ `02888871`（含 PR#22 Q1+Q2）。  
**方法论**：Poteto/pstack — 验证闭环、证明单元、禁重建世界、矫正层级；见 `NOMI-ACTIVE-PROJECTS-20261105.md` §0。

## 角色

| 角色   | 模型                                                              | 任务                                        |
| ------ | ----------------------------------------------------------------- | ------------------------------------------- |
| 作者   | ZCode **GLM-5.3-Flash**（最高推理档可开；权限完全访问须逐次确认） | 唯一产品写者；新 SID，不复用旧 T02/T04 会话 |
| 对审 A | **MiniMax-3.1-Flash / xhigh**                                     | 冻结候选后独立审：正确性/数据 + 验收覆盖    |
| ROOT   | Nomi / Kaiming                                                    | 范围、合并、远端；不代写产品                |

记作 **临时 L2-lite**（两边 Flash）；条件闭合仍人工记清单。不自动 merge。

## 范围（只做 Q3）

从保全的旧 `ffc6fc35` 有界提取「同快照图」8 路径增量，接入真实 develop 新 feature 分支：

- `QueryResultPanel.tsx` 图相关 hunk（勿整文件覆盖 Q1+Q2）
- `result-graph.ts`、`typed-results*`、CSS、类型
- `tests/unit/t04-result-graph.test.ts`
- `tests/e2e/t04-query-variants.spec.ts` 图相关增量

**禁止**：改 main/preload/IPC/contracts/Store；覆盖 T02 `query_presentation` 供给；为行数删 SSR/图断言；Q1+Q2 回滚；静默尺寸例外不记账。

若必须再拆：先交夹具重构方案（保全全部断言），ROOT 签票后再拆。默认 **一批交付**。

## 证明单元（验证优先）

1. 预检：新分支自 `02888871`；旧 ffc6/三提交/overlay 保全；防回退 blob 核过
2. `npm run check` 自然 0
3. 图单测 + 适用 E2E（含保存重开链与图场景）；配置不改 timeout/retry/集合
4. 冻结 base/head/tree + 精确 diff + 命令/退出码索引
5. 推送/draft PR/完整 CI/merge：**仅 ROOT 另票授权**；本 Goal 默认停在「本地验证 + 对审闭合」

## 交付索引必含

- 实际 SID / 模型 / 工作树路径
- 相对 develop 的文件列表与行级摘要
- 未测项与风险
- 对审意见与处置

## 明确不做

Windows C1 主切片叙事；ACK/Linux；OP016；I05/I06 冒充完成；Cloud Agent；公仓躲 Actions。
