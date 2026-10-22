# Round 2 scope 对账与上轮缺读导航

本次仅固定索引/原报告静态文本处理，没有审查产品语义或运行任何setup/产品/测试。两新任务仍须按c1e44/da1795完整工程、新旧历史和全部需求独立审读，不是补缺读后继承旧Pass。

## 173→180真实映射

原173条全部仍为engineering；无删除、无分类变化。138非docs保持138；docs工程35→42。173中171旧blob未变，两处probe/test改blob。新增7项都是真实docs工具/配置，必须纳入，不存在猜测的排除7项。

| 新增路径 | bytes | Git blob |
| --- | --- | --- |
| docs/reviews/T03/mapping-p2-boundaries-20261023/independent-review/audit.py | 8583 | `b8f311579e8cd372781a4605c63b64b536aad008` |
| docs/reviews/T03/mapping-p2-boundaries-20261023/verify-packaged-boundaries.py | 11054 | `b675d1913ed1129b28ca3db84227083f240e9fec` |
| docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/.gitattributes | 87 | `e4e939d2d5e4a74c5318c98d97c8cd0aca70b695` |
| docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/owner/freeze-scope.py | 4553 | `0df752d5c81b123ce085273f316861e616ccb6df` |
| docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/owner/make-dispatch.py | 5006 | `e23e6754dc2fbd808ed607ff225fc48e07afab9f` |
| docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/owner/prepare-environment.py | 4289 | `2c6dd37e4b8ce8aeebc2f0a69f120e1bc4cea8ee` |
| docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/p2-original-raw/build/mapping-p2-boundaries-20261023/run-command.py | 4711 | `d3a57541fc9fcbf55ce1463e1da91b315f044b89` |

全部173逐项old/new与180完整清单见engineering-173-to-180.json。AGENTS tracked1056B仅Git身份，15147B/de15保护overlay另列，不能把两者混称。

## Z自身缺读：15 unit + 5 e2e全部保留

Z原稿第59行声称14 unit，但索引除明确全文t03-mapping-state后有15候选；哪一件另已全文UNKNOWN，不能猜删一项。全部15保留新读任务。

以下只给静态阅读任务，禁止执行测试或native helper；各精确blob/EOF行数在zcode-own-prior-gaps-eof.json。

- `tests/unit/binding-regressions.test.ts` → 1–EOF。
- `tests/unit/contract-v2.test.ts` → 1–EOF。
- `tests/unit/contract.test.ts` → 1–EOF。
- `tests/unit/csp.test.ts` → 1–EOF。
- `tests/unit/engine-connection-state.test.ts` → 1–EOF。
- `tests/unit/engine-environment.test.ts` → 1–EOF。
- `tests/unit/jsonl.test.ts` → 1–EOF。
- `tests/unit/native-driver.test.ts` → 1–EOF。
- `tests/unit/supervisor.test.ts` → 1–EOF。
- `tests/unit/task-progress.test.ts` → 1–EOF。
- `tests/unit/task-runtime.test.ts` → 1–EOF。
- `tests/unit/task-service.test.ts` → 1–EOF。
- `tests/unit/task-update-boundary.test.ts` → 1–EOF。
- `tests/unit/view-navigation.test.ts` → 1–EOF。
- `tests/unit/window-recovery.test.ts` → 1–EOF。
- `tests/e2e/csp-lifecycle.spec.ts` → 1–EOF。
- `tests/e2e/desktop.spec.ts` → 1–EOF。
- `tests/e2e/i04-jobs.spec.ts` → 1–EOF。
- `tests/e2e/native-driver.ts` → 1–EOF。
- `tests/e2e/native-recovery.cjs` → 1–EOF。

其他明确partial/身份级（完整到EOF或完整结构语义，不按上轮片段封顶）：

- `apps/desktop/src/renderer/src/task-presentation.ts`：STRUCTURAL；Z称纯展示映射结构读；完整内容语义仍须从1至EOF。
- `packages/contracts/v2/schema.json`：STRUCTURAL_SAMPLED；Z仅键/枚举/关键defs抽验，非完整载荷语义。
- `packages/contracts/v2/fixtures.json`：STRUCTURAL_SAMPLED；Z仅键/枚举/关键defs抽验，非完整载荷语义。
- `packages/contracts/v2/binding-regressions.json`：STRUCTURAL_SAMPLED；Z仅键/枚举/关键defs抽验，非完整载荷语义。
- `packages/contracts/v2/frame-fixtures.json`：STRUCTURAL_SAMPLED；Z仅键/枚举/关键defs抽验，非完整载荷语义。
- `scripts/i04_matrix_evidence.py`：STRUCTURAL；Z结构级，未完整语义读。
- `uv.lock`：IDENTITY_ONLY；锁字节身份相同不等于完整依赖/锁语义审查。
- `package-lock.json`：IDENTITY_ONLY；锁字节身份相同不等于完整依赖/锁语义审查。
- `design/prototypes/OntoLearn-Studio-Prototype.pen`：STRUCTURAL；结构/身份级；完整结构语义可按实际方式登记，不因设计资产自行删范围。
- `docs/architecture/0001-desktop-framework.md`：STRUCTURAL_OR_PRIOR_SCOPE_UNSPECIFIED；Z称ADR0001/0002/0003/0004未逐字读；按索引实际路径保留，不能猜不存在的ADR0004路径。
- `docs/architecture/0003-resident-coordinator-and-jobs.md`：STRUCTURAL_OR_PRIOR_SCOPE_UNSPECIFIED；Z称ADR0001/0002/0003/0004未逐字读；按索引实际路径保留，不能猜不存在的ADR0004路径。
- `docs/iterations/I01/ADR-0002-storage.md`：STRUCTURAL_OR_PRIOR_SCOPE_UNSPECIFIED；Z称ADR0001/0002/0003/0004未逐字读；按索引实际路径保留，不能猜不存在的ADR0004路径。
- `docs/iterations/I03/ADR-0003-design.md`：STRUCTURAL_OR_PRIOR_SCOPE_UNSPECIFIED；Z称ADR0001/0002/0003/0004未逐字读；按索引实际路径保留，不能猜不存在的ADR0004路径。
- `docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/control-snapshots/plan.md`：STRUCTURAL_REGISTERED；Z称plan/tasks/controller-handoff/review结构登记；须读固定快照全文，旧STOP路径只作历史来源。
- `docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/control-snapshots/tasks.json`：STRUCTURAL_REGISTERED；Z称plan/tasks/controller-handoff/review结构登记；须读固定快照全文，旧STOP路径只作历史来源。
- `docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/control-snapshots/controller-handoff.md`：STRUCTURAL_REGISTERED；Z称plan/tasks/controller-handoff/review结构登记；须读固定快照全文，旧STOP路径只作历史来源。
- `docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/control-snapshots/review.md`：STRUCTURAL_REGISTERED；Z称plan/tasks/controller-handoff/review结构登记；须读固定快照全文，旧STOP路径只作历史来源。
- `docs/reviews/T03/mapping-p2-dual-review-preparation-20261023/legacy-fixed-package/coverage-matrix.json`：STRUCTURAL_PRIOR_SCOPE_UNSPECIFIED；Z称1.1MB历史矩阵结构级并引用既往轮次；本轮完整关系与字段语义须重新覆盖。

Z称约25个历史docs工具登记但未给名单；旧engineering docs35中仅T03旧verifier明确全文。其余34候选全部逐path列出，哪9另已读仍UNKNOWN，不能猜删；完整允许历史docs848逐path也保留。ADR0004未在固定索引发现对应文件，登记UNKNOWN而非创造文件名。

## M自身153 notFULL

minimax-own-prior153-notfull.json逐path原样保留144 METADATA、8 PARTIAL、1 UNREAD及原note（空note仍空，不补造理由）。此前27 FULL同样须在新任务重新全文语义读；153不是新的完整范围。

## 当前材料分发规则

最新根授权允许把241711封存的两个上一轮completed原报告和29项台账共同作为两新任务的历史输入；覆盖旧combined不发限制。本轮任何新peer意见/进度/raw/metadata仍严禁读取和互传。旧报告的本轮一词按其历史时点解读，不能误当新Round2禁读该已授权历史。

当前只准备输入：未创建task/CUA/Goal、未安装、未执行产品/mock/setup/测试/包/native/库；STOP/private payload没有读取扫描。主会将写full prompts，本scope作者不自审最终提示，应另由独立agent审稿。
