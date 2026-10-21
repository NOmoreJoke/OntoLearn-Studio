# T09 实际状态

当前续接工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-stage-evidence`，分支 `feature/weekly-t09-stage-evidence`。共享批准base仍5f910b5，本线续接parent74b17a4。独立私有阶段证据实现固定 `12699cc0f536f5875e8b021349b58c2c954145cc`；当前专项80项通过，最终完整检查与独立报告见本轮证据。T09原Goal保持active。

总控已登记此独立父任务树；原 `T09-learning-baselines` 的S1实现7659665及流程74b17a4冻结，后续只有d96924e文档澄清，没有源/测试变化。S1仍待总控审查预约和指定双模型。此树未采用其他线未批实现，不改公共契约、Store或业务接线。

阶段证据原型只验证受信owner计划/账本、实际canonical job/result/pages与版本、顺序、祖先及原始完成回执。它保留当前真实stale状态，末阶段必须仍current，且再次核实际当前计划。没有操作完成/独立迁移成功/领域passed授权。T01持久不可变完成账本与真实当前输入/epoch/CAS、T00批准接口和领域结果比较均仍缺，未注册或接入LearningService/UI。

当前80项包括2项真实批准I04存储、编辑失效和分页探针；test.read只保存给定rows、学习账本为测试内存对象，不能登记SPARQL/SHACL或学习持久化完成。第一版3项错误码预期失败、完成证明加入后1项fixture绑定失败、首次真实I04探针2项marker键失败均保留；独立审查根输入版本缺失P2及validation样例覆盖不足已修，修后80项通过。说明与owner精确需求见 `docs/iterations/T09/stage-evidence-contract.md`。

以下为继承的T09-S1阶段记录和完整父任务门禁，当前多阶段续接以本节及本轮stage证据为准。

## T09-S1 冻结阶段记录

2026-10-21（Asia/Shanghai）。阶段：独立实现/内容、I04真实基础设施联验、独立学习UI及当前范围内审已完成；尚未正式业务接线、指定双审或合并。独立 Goal 保持 active。

## 身份与文件责任

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-learning-baselines`
- 分支：`feature/weekly-t09-learning-baselines`
- 批准 base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；初次实现提交 `51cdc0e9d138c98cdd4ace865074a71883657a68`；本轮修后检查点见 recovery.json，固定manifest未变。
- 启动实查：`pwd`、`git status --short`、`git branch --show-current`、`git rev-parse HEAD`、`shasum -a 256 AGENTS.md`；启动只有指南未暂存修改，无任务路径冲突。
- 指南现 SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`（总控授权追加政策，旧 SHA db1fb184…保留于历史证据）；保持未暂存、不入产品提交。实际全文接收见 operation-policy-receipt.md。
- 仅新增授权的 content/learning、tests/fixtures/product-baselines、learning 私有 Python 包、test_learning_*.py、固定验证脚本与本任务 docs；后续获总控明确授权的 renderer/src/learning 与 tests/unit/learning-*.test.ts。未改共享 Store/worker/协议/契约/main/App/依赖锁或总控状态。读取最新总控回执确认 storage.py 后续唯一 owner 为 T01，未采用其未批准实现。
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
- `uv run --frozen pytest packages/engine/tests/test_learning_baselines.py packages/engine/tests/test_learning_service.py packages/engine/tests/test_learning_jobstore_integration.py -q`：当前42项通过（原35项加7项I04真实通道），含四套真实临时SQLite完整重建与拒绝覆盖、真实RDF解析/固定查询输入探针、错误对象/顺序/版本/依据及辅助归因负例。合成adapter单测不计产品领域通过。
- `npm run check`：最终完整通过；630项vitest、1094项pytest、lint/格式/类型/构建/ruff均通过。没有新增依赖或打包/主进程改动，未触发额外 package/e2e；未运行本机 GUI/native/HMR，未启动打包产物。
- 独立 agent `/root/t09_prd_audit` 实际只读内审明确通过当前范围；四项发现均修复并读回，见 independent-review.md。
- 首次ruff格式问题原件与首次全check失败原件保留于 evidence。首次全check原文以 first-npm-check.txt.gz 无损归档，原文字节SHA在 verification-summary.json，解压可完整读回。首次全check运行中我修订了fixture，未及时刷新manifest，27项因digest mismatch失败；它不是最终候选验证。随后冻结文件、刷新manifest、重跑35项及完整check通过。无CI artifact可存放前，原件随恢复提交保留，便于复核首次失败和修复，避免覆盖失败证据。

## 未完成与精确下一步

- T01：学习记录schema/受信CAS/持久化；产品案例创建/确认；使用当前批准 Store 能力接入。T09测试重建不替代产品接口。
- T00与T02–T07：批准命名业务桥与实际解析/查询/验证/推理/行为/轮次适配；多阶段检查记录每阶段实际输入/快照/依据，拒绝历史改贴当前与迟到跨尝试混用。
- UI：总控已授权独立 renderer/src/learning 与 tests/unit/learning-*.test.ts，组件已独立实现；主App/bridge、持久化与实际领域工具仍由原owner接线。私有模型与恢复要求见 learning-ui-contract.md。
- 内容入包：请唯一owner评估 `scripts/build-engine.mjs` 等实际资源入口，将 content/learning、固定fixture与对应PRD来源绑定资源纳入最终包或批准等价的只读内容布局；当前repo-root读取不能当作包内资源验证。
- T08实际完整代做来源及T10实际学习报告导出联验；真人至少5人/80%、Windows/macOS完整离线案例验收仍缺。
- 请总控预约本精确工作树候选的 ZCode GLM-5.3/最高及 MiniMax M3.1-Flash/xhigh 两个全新独立只读完整审查。当前预约仍由I05占用，未抢用应用、未伪造报告。
- 最终依赖批准后刷新实际base、集成/联验、同版指定双审通过才push/PR/CI/merge。当前未push、未建PR、未合并、未上线；T09父任务与完整产品发布门均未关闭。同一聊天继续后续修复/接线/双审/合并。

## 本轮 Goal 续接与真实通道修复

上一轮为实际进展：已保存独立实现与恢复提交。本轮复查总控，批准base仍5f、指定审查资源仍预约I05，未取得正式域/页面路径放行；没有据此采用未批准代码。

本轮继续完成T00建议的第一条基础设施联验：四套固定输入经JobStore真实回滚预览、实际stdio coordinator/worker、test.atomic提交、operation/result.page及重开完整读回。首跑4失败/3通过，实际暴露seed包装ID冒号导致Project协议不合法；已只修私有helper为协议允许名称，并核对完整Project/依赖向量。修后7项通过；当前42专项和完整check（630/1094）通过，独立agent重建复核通过。失败原文无损归档和当前SHA见 `evidence/jobstore-verification.json`，不以原先35项Store测试掩盖这个新发现。

当前基础设施通道通过不等于正式业务接线。旧包装ID的导入器不得被T01引用；原始固定输入/manifest可继续固定只读使用。已从规划聊天实际read_thread核对人类“发送并落实到现有总控”授权，精确来源见 coordination-authorization.json；已通过 send_message_to_thread 实际发送本线修后873c8c0交付与精确资源需求，工具成功，见 controller-delivery.json；总控随后已实际读取并回执873内容/通道证据，明确授予独立UI路径；指定审查预约仍待资源放行，不将发送成功当批准。


## 独立学习 UI 续接

已在总控后续授权路径实现离线课程、九任务导航、四级提示、术语与常见错误、真实结果反馈投影、学习报告回执入口和响应式样式；没有编辑共享路由/bridge/main/preload或依赖锁。组件只读静态内容，真正的学习记录、工具调用、报告导出仍是外部受信 owner 的能力。

独立内审发现并修复：真实context缺保存能力时不展示提示；较新记录不能降低最高辅助，同版本冲突不能计完成；同一尝试换输入仍保留辅助；矛盾新版本不能回退使用旧独立通过。迁移题无真实尝试时不展示任何级别答案，拒绝未记录预览后计算独立成功。当前输入/任务/尝试/项目/窗口生命周期迟到回执隔离。

`ui-first-vitest`/`ui-second-vitest`分别是内存入口和缺少匹配浏览器失败；`ui-third-vitest`为16纯通过、13组件失败，统一JSX开发/生产运行时不匹配。`ui-fourth-vitest`30项通过，但后续归因防御与新增测试后不将其冒充最终候选。首次全check浏览器自带JS被lint扫描、随后Vite8配置类型失败也保留原件；运行时移至本树被既有规则忽略的node_modules子目录，并使用安装版支持的OXC选项，未弱化lint/类型/测试门禁。

最终UI候选完整检查与独立内审结果见 evidence/learning-ui-verification.json 及 learning-ui-independent-review.md。截图为私有组件headless结果，不能代替正式Electron、实际领域/持久化、包内资源或真人验收。正式接线、指定双审、CI/远端及发布门仍未关闭。

最终冻结实现 `76596656908ed84e577e8202a602e3256d5febcc`：显式启用独立headless运行时的完整 `npm run check` exit 0，664项Vitest（18学习纯逻辑+16学习headless组件）、1094项Python及lint/格式/类型/构建/ruff均通过。1440与390px截图已实际查看，窄屏无页面横向溢出；输入与反馈均以React文本渲染，测试观察网络请求0。浏览器证据仅支持chromiumSandbox:true配置和成功运行，未采当次argv/OS sandbox状态和二进制hash，不当作原生平台隔离证明。此前失败/中间结果均无损gzip保存并绑定原始字节SHA，不能替代最终候选。

总控固定765/74审计的文档口径已修：T09_HEADLESS_UI未设1始终skip，与runtime是否安装无关；设1缺匹配runtime是启动失败。手机截图文件390×1932，采样viewport390×844，两者分别记录。历史74提交和原始交付回执原样保留，本次仅文档澄清，不触发无变化产品重测。

本轮最终固定12699cc同版 `npm run check` exit0：648 Vitest通过、16 headless明确skip、1174 pytest通过，lint/格式/类型/构建/ruff均通过。80专项及实际I04限定探针含于完整Python运行。没有重复执行未变UI浏览器套件，不将skip算通过；旧S1的18纯+16显式headless证据仅支持其固定候选。当前源/测试三文件commit后无差异，失败及中间证据无损归档。

固定12699cc私有范围独立内审明确通过，两项P2（根输入版本/文本身份校验与validation类型覆盖）已关闭，见 stage-evidence-independent-review.md；此结论不替代真实持久化/领域集成或指定双模型。
