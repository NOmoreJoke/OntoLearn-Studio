# T04-S1 指定审查当前执行补充

2026-10-22。来源为总控聊天 `01a154de-843b-7a00-8a80-51ba1c0aebce` 本轮实际 setup 通知：原 T04 是两个独立 review 树的唯一 setup owner；本补充只改变审查运行与输出边界，不改变产品、测试、依赖、验收或 base。它不是 T04 GUI lease、任务创建、指定通过或 Goal 恢复。

## 优先关系

旧 `round-1` 两份原始完整 prompt、manifest、AGENTS/common/后台路线快照保留原字节，属于历史输入。新投递正文必须完整包含原 prompt 和完整 S1 范围，并附精确 workspace 映射与当前 AGENTS/common/桌面政策、本补充。实际执行以新正文的映射和本补充为准：替代旧 prompt 的“任何验证即使有新风险也只能申请”“只能写单一报告文件”“禁止当前桌面/必须后台或独立桌面”等过时操作限制。审查范围、模型、原需求与质量门不得缩小。

## 独立环境与允许验证

- 两审者各使用自己实际登记的独立 detached review 树、node_modules、.venv、构建/cache/tmp、反例、raw 和报告。只能读取本方完整输入和共同原件，不读取另一方本轮 prompt、反例、日志、报告或意见。不得共享可变运行目录、结果库或审查结论。
- 原 T04 setup owner 可按原锁独立 `npm ci --ignore-scripts --no-audit --no-fund` 与 `uv sync --frozen` 备环境；安装本身不算产品验证，不自动运行 build/test/Electron。两环境已备好，审者不得为安装/修环境改源、锁、依赖或全局认证；依赖缺失保留真实错误，交唯一 setup owner 处理。
- 两指定审者可自主进行与固定候选对应、为其独立判断所必要的普通静态检查、单元测试、SSR、check/build 及普通受控测试 worker 回归，不需因旧过宽限制再次请求这些普通验证。先静态读取准确 script/config/测试文件及其子入口，核清 cwd、输入、输出、资源和进程归属后运行。不机械重跑所有不变历史；若其独立判断需要正常完整 check，可运行并保留真实结果。
- 准确的候选入口包括 `npm run lint`、`npm run format:check`、`npm run typecheck`、`npm test -- tests/unit/t04-query-authoring.test.ts tests/unit/t04-query-results.test.ts tests/unit/t04-query-reader.test.ts`、`node docs/iterations/T04/ssr-probe.mjs`、`uv run --frozen pytest packages/engine/tests/test_query_service_authoring.py packages/engine/tests/test_query_service_approved_baseline.py -q`、`npm run check`、`npm run build`，以及静态核过的普通原有测试 worker 回归，例如 `uv run --frozen pytest packages/engine/tests/test_worker_parent.py -q`。这是普通验证运行面，不证明所有入口已由本次 setup 执行。
- `npm run check` 的准确链为 lint → format:check → typecheck → vitest → build → engine:check（ruff/format-check/pytest）；vitest 配置仅含 `tests/unit/**/*.test.ts`，desktop build 是 `electron-vite build`。这些名称本身不是安全证明，审者仍需检查其实际子入口。`npm run dev`、HMR、`test:e2e`、`package:dir`、自动启动 Electron/产物及新的 native/caller/producer 不在本次普通 S1 验证运行面，不能借通用桌面授权自行扩成新验收。
- 可在本方 ignored `test-results/t04-review-runtime/<role>/` 写独占反例、raw、运行收据、缓存、临时数据；也可由正常 check/build 写本方原有 ignored out/dist/build、.pytest_cache、.ruff_cache、__pycache__ 等常规产物。最终报告只写映射明确的本方 `docs/reviews/T04/round-1/<model>.md`。反例不能写进源或原测试目录，不能改变验收真值，也不能成为第二执行器/Store/公共 schema。
- 每次实际运行记录完整 argv、cwd、起止时间、真实 exit code/超时/信号、完整 stdout/stderr 原件与哈希，保留首失败及后续结果。禁止 skip/xfail、删除或削弱断言、改输入真值、失败后筛掉失败项冒充整套通过。精确路径定向验证可做，但必须说明它的范围，不能冒充完整 check。只清理本方已核 PID/进程树，不宽泛结束用户/其他任务进程。

## 仍禁止的研究与修改

源码、原测试、配置、锁、Git 状态/提交/分支、冻结旧输入、原验收和其他报告全部只读；AGENTS 仅由阶段主聊天传播为保护 M，审者不格式化、覆盖或提交。不得 `git add/commit/push/reset/checkout`、修改共享契约、写第二可变源或消费未批准实现。

已被拒绝的 SQLite 损坏/heap/OS 研究、SQLite 损坏 HOLD、未签运行票、new native/caller/producer、外部 API/新增付费和密钥读取/搬运继续禁止。普通受控 worker 测试不扩张为新破坏性研究；必要的临时测试库只在该测试自己的 tmp 路径，不能触及用户或其他任务数据。若精确入口实际包含被 HOLD/拒绝的工作，不擅自排除后宣称整套通过，报告该入口未运行/阻断及对应原授权边界。

当前 S1 无 App 正式接线，审者可用独占反例证明其实际缺口；标准库/合成 transport/SSR/普通 worker 不能冒充真实业务 IPC、Store 保存、query.execute、平台、真人或完整父功能验收。

## 桌面、模型与终态

人类已撤回静默桌面要求；已授权 computer use 不再需要用户桌面时段、独立桌面或 CLI 登录前置。原功能 owner 只在总控内部短 lease 中操作审查应用创建、设置和核验；后台推理不占整个桌面时段。本线当前尚未获得 GUI lease，不能启动 T04 任务或抢 T01/T06 资源；这不阻止当前静态输入和环境准备。

ZCode 固定 GLM-5.3/最高 max/yolo，MiniMax 固定 M3.1-Flash/xhigh/bypassPermissions。每方本轮新完整独立任务，同一 base/product，逐任务实际 provider/model/可用等级/思考/权限/工作区读回。无设置/任务 ID 时不能假填。完整终态、全文报告、所有意见处置、同版双方明确通过及原验收、push/PR attach/实际 CI/正常 merge/远端门保留。不得拿安装完成、目录存在、旧内审或另一方意见当本方指定通过。
