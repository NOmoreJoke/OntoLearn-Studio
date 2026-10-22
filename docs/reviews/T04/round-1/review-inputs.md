# T04-S1 round-1 冻结输入清单

2026-10-22；仅准备，未创建指定任务、未授 T04 lease、未投递正文、未产生指定报告。原 Goal 保持 blocked。

- 原工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query`。
- 分支：`feature/weekly-t04-query`。
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；product head：`554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`。
- 本包准备前 process head：`e761d2962aa18c83885dde4cc0dcd15fd9aba322`；本包所在过程提交由开发线提交后单独回执，不写自引用 SHA。
- 全部 base→product binary diff：170428 字节，SHA-256 `777ef6d58b8697530024ad4c47110443b613b9ba7de37d8420fae97e44b6c651`，共 33 个新增文件；`git diff --binary <base> <product>` 可从 Git 原件重建，不能用仅 UI 或部分 stage diff 替代。
- 原 33 项 manifest：`docs/reviews/T04/evidence/service-candidate-554ec89.json`，SHA `87136a08763e4bc59322ac04a6a8ef400c39994ba159df6d65c0eebccc6cdbc3`。

## 固定产品的全部输入

以下 33 项都必须从固定 product Git blob 核验并纳入审查。`status.md` 的当前物理文件已追加流程信息；其产品原字节用 `git show 554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6:docs/reviews/T04/status.md` 读取，后续当前状态另读固定 process 版本，不能声称当前物理 33 项全等。

| 路径 | 字节数 | SHA-256 |
| --- | ---: | --- |
| `apps/desktop/src/renderer/src/query/QueryPage.tsx` | 26550 | `984eeeb985a6d47a392b474769664de5c3b8d2383303d24160f5381d5b1f930a` |
| `apps/desktop/src/renderer/src/query/draft.ts` | 5394 | `c4289a019ff4ee2f1d5bfb69c1d285c6a25ddf8f0223aa148e301f6f1d1dbdf7` |
| `apps/desktop/src/renderer/src/query/query.css` | 2104 | `29c062a96247082058c20cb4c1667dc5f552f92fb5ec28f425943e465c1c6b03` |
| `apps/desktop/src/renderer/src/query/reader.ts` | 14095 | `4223086b299695a22b5b978ff1475634910d840df7b0304183c9db2e725e15b6` |
| `apps/desktop/src/renderer/src/query/results.ts` | 4100 | `18aba90ff6867c6e83ae8b04222225180454b519065f8e9b4992270f14adc21d` |
| `docs/iterations/T04/acceptance.md` | 4718 | `98278b69d70d50842118a3e31286e62b3c9f1928e78a3cb78afb098a64b89e2c` |
| `docs/iterations/T04/integration-handoff.md` | 6731 | `f0be676e38551714dcb923e890351a4f946ee514c8548910381c1fd2005600d1` |
| `docs/iterations/T04/reader-integration.md` | 4596 | `b4f8d629da598efe980f2bfc13527d42f5eea2eaa7e0b6de9275c11c5cd82373` |
| `docs/iterations/T04/ssr-probe.mjs` | 6293 | `865105b1b8ac2497c6ee6492c07d59a1f5baccea4a713a135829f586e61f4f47` |
| `docs/reviews/T04/evidence/final-verification.json` | 3584 | `ff19302876ecb5ae674a385c2747395b6a94cfb50afc757a567c96ccf3361ea4` |
| `docs/reviews/T04/evidence/verification-summary.json` | 1677 | `333ba970baaac6a1cb2978415a7e9fec366663784334e1190883feec3845ac8f` |
| `docs/reviews/T04/internal-candidate.md` | 1979 | `334309aeab5e0609de09b9bf7d06f24babe6dfd64481453c4f50fe0095747385` |
| `docs/reviews/T04/internal-review-1.md` | 2377 | `b753302708bb81555ed1055b8ed308b761c41c259848c3782786bc9c03c50a86` |
| `docs/reviews/T04/internal-review-2.md` | 1479 | `1503db4ffa611e737e582c3258c3045f0aa84bcc858f742e2c76ce372a775459` |
| `docs/reviews/T04/internal-review-3.md` | 1184 | `73af84c133257e2453c52c1d8d3bd986b1c457366e70dcc7c2c42b89586f54e5` |
| `docs/reviews/T04/internal-review-4.md` | 1166 | `df16eed19f066af11af47c5e0a066f450b8654c5e65e9af5965eb17756f37353` |
| `docs/reviews/T04/internal-review-5.md` | 2333 | `7e962fd421a46a0ced0cdeb805f57a998e4d3cf2c0b952a6d00082e3821d53ee` |
| `docs/reviews/T04/internal-review-6.md` | 1566 | `754b3867bcaa0635a6fe698193c5e91855184eb6df112324f47e9c7916eae066` |
| `docs/reviews/T04/internal-review-7.md` | 1264 | `239f33253b11abafb5b8f9357712e650cecdfb4ee810f92313107afeb50f1b10` |
| `docs/reviews/T04/status.md` | 5541 | `237f2343cedd685b27bc8d316af7f0a26d9a5a3469f395dcfb5d637b8de3662c` |
| `packages/engine/src/ontolearn_engine/query_service/__init__.py` | 249 | `5d845de6372420810d86d77ca53cb2f425b884a703fbbe9f9c5ae004eeb815ed` |
| `packages/engine/src/ontolearn_engine/query_service/drafts.py` | 5786 | `829f77805c1039f961092b6353e72c8bfc503becd011ebe772a85ce96d28ac84` |
| `packages/engine/tests/test_query_service_approved_baseline.py` | 3561 | `6d3405076b9cc269cfefbb0859d213d1300652a3c4aa8f9aa49ac327ee9be588` |
| `packages/engine/tests/test_query_service_authoring.py` | 5347 | `fbcc30702d518f035d9a3d678959bab2acba3dd28e82dffc07b8b0878f417a1b` |
| `tests/fixtures/query/approved-baseline/G-base.json` | 8219 | `306d41b332d223b47929eb90f196c71e4965a0e9ff81100c9469ed32612e8845` |
| `tests/fixtures/query/approved-baseline/conventions.json` | 1165 | `26c03d12be2ea4f0e09c15f8bc1ade161233487f254da0c947f680ae9f533b47` |
| `tests/fixtures/query/approved-baseline/manifest.json` | 2268 | `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e` |
| `tests/fixtures/query/approved-baseline/provenance.json` | 2576 | `08d501a3c2d1080bbaf752a2ea1c84b35fa8738b99faccfe331827343e283366` |
| `tests/fixtures/query/approved-baseline/unclosed-high.rq` | 162 | `8efbacd589c42ac40abbb55475cdd088e407a88a23e0db61dc8375e04e4dd386` |
| `tests/fixtures/query/authoring-case.json` | 1574 | `34b8feb9b470f50ce9cf45080f045b80163f2871a3fdb050860921cb05e6d4bc` |
| `tests/unit/t04-query-authoring.test.ts` | 3585 | `0c1ccaf92044f5cb65fa445b62e0830ff8f8e6af99b29d874c7919066e3b769f` |
| `tests/unit/t04-query-reader.test.ts` | 20549 | `52e6283de1c6759ba40dd8a0ac210f13ed7f77c7efcb158ae1fb83d1f9800372` |
| `tests/unit/t04-query-results.test.ts` | 5462 | `e275b48c17d3c46723fe2c229cf145c419334006cc693d1261816f5f96b25b68` |

## 只追加的支持证据与政策

机器索引 `frozen-input-manifest.json` 固定全部产品和支持文档来源、字节/哈希及提示原件；该索引自身的哈希由提交后回执另给，避免循环。

- `docs/iterations/T04/service-stage.md`：总控已登记的完整 S1 范围。
- `docs/reviews/T04/internal-review-8.md`：最终固定 554 独立内审，连同全部 1–7 阅读。
- `docs/reviews/T04/evidence/reader-service-verification.json`：最终 554 全 check 汇总。
- `docs/reviews/T04/evidence/raw-logs-554ec89.{tar.gz,index.json}`、`raw-logs-recovery.md`：37 原日志恢复及版本来源，总控 R1 已实际关闭。
- `docs/reviews/T04/status.md`：只读准备前 process e761 的后续状态，区分原件与晚出回执。
- 本目录 `verification-and-history-index.md`：实际验证归属和每项历史发现/处置/关闭；不是本轮指定模型结论。
- 本目录 `operating-policy-snapshot.md`：完整共同指令原字节，SHA e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0；历史归属文字按末尾已生效补充解读。
- 本目录 `protected-guide-snapshot.md`：保护 AGENTS 原字节 SHA 78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759；原工作树 AGENTS 保持未暂存。
- 批准 base 的 `docs/prd/PRD-本体学习与落地Agent工作台.md`：对应 FR-400–404、FR-006、C/D/G Q-01/02/O-01、第11–12节；源 SHA 7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb。
- 批准 base 的现有 contracts、任务模板/命名 bridge 和 Store 文件可只读用于接口核验，不将未批准 T01/I05/I06/T08 代码作为依赖。T09 仅采用已批准 873c8c051b9870aa12fc7e1dbbd3e0c358e7c380 输入原件，provenance 保留。

## 实际 workspace 与后台入口

当前没有新建 review 工作树，没有实际 provider task ID。原树/分支/base/product 是上面的原件来源，不是已启动外审的声明。实际后台创建只在总控授予 T04 独占 lease 后由本线执行；当前 T06 是后台入口恢复唯一 owner，不竞争其任务。

已支持路线原件为仓库外 `iteration-control/2026-10-21-weekly-release/T06-supported-background-external-review-window.md`，本包原字节快照 `background-route-snapshot.md`（5446 字节，SHA `9a2d722dc86c64d66929cadd12631cc85042bdd820aba9ec76de882fa3ed5de4`）。外部源仍可继续更新，本包只固定已全文读到的该快照，不要求外部可变文件永远同 SHA。它证明可尝试的官方后台路线，不证明登录、任务、可用模型或 T04 lease。不得使用 GUI、未知 HTTP、手写任务库或读取密钥绕过。

若日后另建固定 review workspace，必须另追加映射收据：实际绝对路径/分支/HEAD/base/product 全 diff hash、33 源字节、支持证据、唯一报告写入路径及核验结果，单独 hash 后随任务投递。两份原提示和本包原件不改；不把错误目录的最后选择当作正确 workspace。映射缺失或 byte/identity 不符则停止提交正文，报无法验证。

每方只读自己的完整 input prompt、上述共同输入和历史内审资料，不读取另一方本轮 prompt/报告/日志/意见。共享 manifest 里的另一提示哈希只用于开发线审计，不能当对方结论。外审报告路径当前不存在，不能建立通过/占位报告冒充终态。
