# 本轮实际隔离路径与验证写面addendum（本轮优先于历史packet）

本任务是MiniMax Code / M3.1-Flash / xhigh / bypassPermissions的一轮完整独立只读代码审查；权限设置必须由原开发线在实际任务读回，不凭本提示假定已设置。尚无任务ID或报告，不能创建占位Pass。本任务只在root短lease实际派发后运行，不自行创建其他模型任务。

## 精确运行身份

- 只在此隔离树审查与执行：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90`；Git为detached HEAD `77f2d5048630827ba5220fe092392ded6ab1c697`，不是feature分支，不得checkout/switch/reset。
- 批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；全部产品实现 `c3c7e90f721344113c4279d663127f9c8d5bda59`；固定证据/147项Git输入 `a1e7efef4bd47c97b630753c0e7c4dc34de1d8ae`；工具实现来自66eeedd。当前执行树77与产品C源码/tests/fixtures/锁/CI无差异，77只补流程材料。报告必须区分这些身份，不把a1当实际执行HEAD，也不把当前工作树status追加当a1的相同blob。
- 当前AGENTS为阶段线传播的de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4，受保护且不提交；它只提供当前操作政策。固定代码从Git对象与当前隔离树核验，不读取未批准其他功能实现。
- 唯一最终报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90/docs/reviews/T10/round-1/minimax-m31flash.md`；原packet中主开发树/branch/报告位置只是历史身份，以本段隔离路径为准。不要在主开发树或另一审查树运行/写入，也不要读对方本轮报告/结论。
- 自己的验证原始输出：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90/docs/reviews/T10/round-1/minimax-raw`；自己的可写scratch：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90/out/t10-review/round-1/minimax`，可在其中写独立反例、临时验证配置/夹具、脚本、日志和派生流。已有依赖是此树自己的`node_modules/`和`.venv/`，不得借用其他线的可变环境。

## 明确允许必要验证；替代旧“仅报告可写”过严条款

原packet及旧addendum中“仅MD可写、缓存/派生构建/raw全只读、额外测试一律交原线”的限制已被本轮明确授权纠正。**允许你在本隔离树的独立env/scratch执行原验收所需完整check、复现及独立反例，并写自己的派生验证流**，而不是只看旧summary。可直接运行`npm run check`、必要定向pytest/vitest或独立有界验证；不得通过改现有源码/tests/fixture/锁/配置/验收使测试变绿。

允许写：上面自己的最终MD、raw与scratch目录、自己的`node_modules/`/`.venv/`和cache、正常派生`out/dist/build/release/test-results/playwright-report`与`__pycache__/.pytest_cache/.ruff_cache/coverage`等输出。新独立测试及其临时配置放自己scratch，可明确运行，不写入原tests或fixture。新安装的验证依赖若确需，放自己独立scratch/env并记录版本/命令，不改原package/pyproject及锁。不把自己的派生文件覆盖旧原件。

保持只读：全部受审源码、原tests、fixture、依赖声明/锁、配置、验收、旧raw/截图/manifest、AGENTS和Git状态/索引/refs。Git仅status/show/diff/log等读取，禁止stage/commit/stash/reset/checkout/merge/push。禁止`npm run format`或改源HMR探针；不要修改候选实现“顺便修复”。发现问题写报告，修复由原唯一owner后续新候选处理。

建议给子进程设置各自缓存/临时目录，避免资源混用：`TMPDIR=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90/out/t10-review/round-1/minimax/tmp`、`UV_CACHE_DIR=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90/out/t10-review/round-1/minimax/uv-cache`、`npm_config_cache=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90/out/t10-review/round-1/minimax/npm-cache`、`XDG_CACHE_HOME=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90/out/t10-review/round-1/minimax/cache`；需要的目录可自行创建。不改变HOME/CODEX_HOME或读取全局凭据。每条实际命令/版本/退出/完整原始日志和首失败都记录到自己的raw；不要只留下最后一次绿灯。

历史证据措辞澄清：下方原backlog T-B的“attempt1创建前检查失败”保留原字节，应按原始状态解释为“容器已创建，但启动前CAP名称检查失败”；当时`Status=created`、`StartedAt`为零，从未启动。它不构成一次native运行，更不构成通过。此处仅澄清旧措辞，不修改旧packet/backlog或原始记录。

## 原验收与独立性不缩减

双方都完整审ZIP信封、HTML/页面、文件发布、render-probe与全部六隔离native工具及已保存原件；不是分工只审一半。既有691TS/1112Py、内审2+3P2及native/brower证据是历史证据，不是替代你核验代码/必要复现的Pass。允许完整check和真正独立反例，不人为把验证权限收成空集。

原当前桌面政策撤回静默/用户时段/CLI登录前置，已授权动作可直接computer use；其他原生窗口与桌面互斥资源须与root内部短时协调，不占整个后台推理。仅针对真正必要S1验收提出或运行测试，不能把旧App e2e或隐藏/stub窗口当未接线服务验收，也不能突破未签运行票/自动审批拒绝/SQLite损坏HOLD等原具体边界。没有新GUI验收必要时不无意义启动；这不是静默前置。

无新增付费/密钥读取/搬运/付款或额度确认绕过；不结束用户/其他任务进程。不引入另一个协议、writer、inventory、生产lease或未批准依赖。原父FR1000/1001/104、A06–08/G6、包内/两OS/真人/完整57P0、双审/CI/正常合并/远端仍保留。

报告列实际身份、读过/运行过内容、全部失败及复现、每项优先级/路径行/触发/影响/证据/建议、历史处置与未验边界，最后明确通过/不通过/无法验证本阶段，不给条件Pass或把局部审查扩成完整T10。若实际任务ID未向模型可见，明确未可见，不猜测；原线用真实创建/终态原件关联。每轮各新完整独立任务，不复用旧对话，禁止提前读取/接收/展示另一方本轮报告、摘要、结论或问题清单。
