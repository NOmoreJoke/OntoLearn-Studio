# T09 实际状态

2026-10-21（Asia/Shanghai）。阶段：独立实现/内容、I04真实基础设施联验及独立内审已完成；尚未正式业务接线、指定双审或合并。独立 Goal 保持 active。

## 身份与文件责任

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-learning-baselines`
- 分支：`feature/weekly-t09-learning-baselines`
- 批准 base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；初次实现提交 `51cdc0e9d138c98cdd4ace865074a71883657a68`；本轮修后检查点见 recovery.json，固定manifest未变。
- 启动实查：`pwd`、`git status --short`、`git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256 AGENTS.md`；启动只有指南未暂存修改，无任务路径冲突。
- 指南 SHA 始终为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`；保持未暂存、不入产品提交。
- 仅新增授权的 content/learning、tests/fixtures/product-baselines、learning 私有 Python 包、test_learning_*.py、固定验证脚本与本任务 docs。未改共享 Store/worker/协议/契约/main/App/依赖锁或总控状态。读取最新总控回执确认 storage.py 后续唯一 owner 为 T01，未采用其未批准实现。
- AGENTS 引用的 `docs/architecture/m0-review-and-update-plan-2026-10-19.md` 在批准 base 不存在；已读存在的 ADR-0001/ADR-0002 与本轮真实启动/共同规则、T00 只读提案，未将提案当批准契约。

## 可只读引用的实际交付

- `tests/fixtures/product-baselines/manifest.json`：版本 `prd-v0.6-learning-1`；17 个输入/预期/课程文件的字节 SHA，并绑定原 PRD SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`。
- manifest SHA：`aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`。
- 完整 G-base/G-map-empty/G-behavior 原始模型、固定与失败 CSV、查询、规则/约束/行为、E.5 两产能四轮完整事实/工单/事件消费/轨迹/指标预期。`coverage.json` 保留50条原文，`cases.json` 给出版本化用例计划。跨模块 G.5/G.6 仍需真实适配；A-10完整指定评估集依赖T08，内置三个固定反例不是其完整替代。
- `python3 scripts/verify-product-baselines.py --reset <G-base|G-map-empty|G-behavior|E.5>`：先核验完整manifest，stdout导出独立模型，无项目覆盖、无预置推导。私有 `seed_test_project()` 通过批准 base 的 `Store.commit` 在全新测试项目重建，产品创建/确认仍由T01负责。
- 六模块课程、四级提示、常见错误、23项术语、两项不同数据的迁移任务；学习纯服务真实工具适配缺失时返回待依赖。操作完成、最高提示、完整示范、Agent辅助与独立迁移成功分开；完整代做不计独立成功。
- 精确接口、完整成功/失败输入、阶段证据约束、资源需求见 `docs/iterations/T09/handoff.md`；真人至少5人/80%方案及空记录见 user-acceptance.md，未造样本、未对外招募。

## 实际验证与内审

- `python3 scripts/verify-product-baselines.py`：通过17文件/50案例计划完整性与来源hash，输出 `productRuntime: not-executed`。
- `uv run --frozen pytest packages/engine/tests/test_learning_baselines.py packages/engine/tests/test_learning_service.py -q`：当前42项通过（原35项加7项I04真实通道），含四套真实临时SQLite完整重建与拒绝覆盖、真实RDF解析/固定查询输入探针、错误对象/顺序/版本/依据及辅助归因负例。合成adapter单测不计产品领域通过。
- `npm run check`：最终完整通过；630项vitest、1094项pytest、lint/格式/类型/构建/ruff均通过。没有新增依赖或打包/主进程改动，未触发额外 package/e2e；未运行本机 GUI/native/HMR，未启动打包产物。
- 独立 agent `/root/t09_prd_audit` 实际只读内审明确通过当前范围；四项发现均修复并读回，见 independent-review.md。
- 首次ruff格式问题原件与首次全check失败原件保留于 evidence。首次全check原文以 first-npm-check.txt.gz 无损归档，原文字节SHA在 verification-summary.json，解压可完整读回。首次全check运行中我修订了fixture，未及时刷新manifest，27项因digest mismatch失败；它不是最终候选验证。随后冻结文件、刷新manifest、重跑35项及完整check通过。无CI artifact可存放前，原件随恢复提交保留，便于复核首次失败和修复，避免覆盖失败证据。

## 未完成与精确下一步

- T01：学习记录schema/受信CAS/持久化；产品案例创建/确认；使用当前批准 Store 能力接入。T09测试重建不替代产品接口。
- T00与T02–T07：批准命名业务桥与实际解析/查询/验证/推理/行为/轮次适配；多阶段检查记录每阶段实际输入/快照/依据，拒绝历史改贴当前与迟到跨尝试混用。
- UI：新增学习页面路径需要总控登记唯一责任，主App/bridge仍保留原owner。T09目前授权路径不含renderer，因此未抢写。
- 内容入包：请唯一owner评估 `scripts/build-engine.mjs` 等实际资源入口，将 content/learning、固定fixture与对应PRD来源绑定资源纳入最终包或批准等价的只读内容布局；当前repo-root读取不能当作包内资源验证。
- T08实际完整代做来源及T10实际学习报告导出联验；真人至少5人/80%、Windows/macOS完整离线案例验收仍缺。
- 请总控预约本精确工作树候选的 ZCode GLM-5.3/最高及 MiniMax M3.1-Flash/xhigh 两个全新独立只读完整审查。当前预约仍由I05占用，未抢用应用、未伪造报告。
- 最终依赖批准后刷新实际base、集成/联验、同版指定双审通过才push/PR/CI/merge。当前未push、未建PR、未合并、未上线；T09父任务与完整产品发布门均未关闭。同一聊天继续后续修复/接线/双审/合并。

## 本轮 Goal 续接与真实通道修复

上一轮为实际进展：已保存独立实现与恢复提交。本轮复查总控，批准base仍5f、指定审查资源仍预约I05，未取得正式域/页面路径放行；没有据此采用未批准代码。

本轮继续完成T00建议的第一条基础设施联验：四套固定输入经JobStore真实回滚预览、实际stdio coordinator/worker、test.atomic提交、operation/result.page及重开完整读回。首跑4失败/3通过，实际暴露seed包装ID冒号导致Project协议不合法；已只修私有helper为协议允许名称，并核对完整Project/依赖向量。修后7项通过；当前42专项和完整check（630/1094）通过，独立agent重建复核通过。失败原文无损归档和当前SHA见 `evidence/jobstore-verification.json`，不以原先35项Store测试掩盖这个新发现。

当前基础设施通道通过不等于正式业务接线。旧包装ID的导入器不得被T01引用；原始固定输入/manifest可继续固定只读使用。已从规划聊天实际read_thread核对人类“发送并落实到现有总控”授权，精确来源见 coordination-authorization.json；已通过 send_message_to_thread 实际发送本线修后873c8c0交付与精确资源需求，工具成功，见 controller-delivery.json；实际接收、页面路径授权和审查预约仍待回执，不将发送成功当批准。
