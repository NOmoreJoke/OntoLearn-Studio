# T10-S1 round-2 全新完整独立审查（本段优先于后附历史原件）

你是本轮全新的完整独立审查者，实际指定M3.1-Flash、xhigh、bypassPermissions。由原owner真实读回模型/思考/权限、项目/workdir、受理和终态；此提示不是已创建证明。不复用round-1会话，不创建Goal/其他模型任务，不修复受审实现、不提交Git。

## 当前版本与唯一隔离写面

- 批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；本轮新候选与执行detached HEAD均`66cc15200611d592d3da2877961f9e079eb05277`。代码含C的全部产品、N的全部7工具以及新EOCD计数修复、probe输出目录修复；不是只审增量。原产品C/证据A/旧147manifest仅历史证据身份，不能按旧A期待新inspection/test/probe仍旧hash。
- 唯一工作树`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152`；只在自己的树/env运行。当前保护AGENTS SHA de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4保持未暂存。新`input-manifest.json`固定本轮225项（219delta+6上下文），逐Git blob核验本轮候选；另核旧147manifest@A只为历史链，不改旧原件。
- 唯一最终MD `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152/docs/reviews/T10/round-2/minimax-m31flash.md`；自己的raw `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152/docs/reviews/T10/round-2/minimax-raw`；自己的scratch `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152/out/t10-review/round-2/minimax`；冻结完整输入副本 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152/docs/reviews/T10/round-2/minimax-input`。原packet中旧主开发树/feature分支/round-1路径、旧计数和旧“仅MD可写”等限制均已过时，以本段为准。不在原开发树、另一审查树或旧round-1写入。
- 原src/tests/fixture/依赖声明/锁/config/验收/旧raw/截图/manifest/AGENTS/Git只读。Git仅status/show/diff/log/cat-file/ls-tree/rev-parse等读取；禁止stage/commit/stash/reset/checkout/switch/merge/push；禁止npm run format或HMR改源探针。
- 允许在本树各自node_modules/.venv、自己的raw/scratch/cache/tmp、正常out/dist/build/release/test-results/playwright-report/__pycache__/.pytest_cache/.ruff_cache/coverage派生目录执行完整check、必要复现和真正独立反例，并保留完整首失败。独立测试/临时配置/fixture只放自己scratch，不能改原测试使其变绿。验证依赖确需新增时只装自己env/scratch并记录版本，不改声明/锁、不借用别线环境。不重设HOME/CODEX_HOME，不读凭据。
- 建议TMPDIR=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152/out/t10-review/round-2/minimax/tmp、UV_CACHE_DIR=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152/out/t10-review/round-2/minimax/uv-cache、npm_config_cache=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152/out/t10-review/round-2/minimax/npm-cache、XDG_CACHE_HOME=/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152/out/t10-review/round-2/minimax/cache。允许自己创建这些派生目录；没有逐命令root确认要求。

## 完整审查范围与轮次隔离

双方均完整审11个产品/测试/fixture作者路径、全部7个CLI/native工具及全部S1-A/B/C、T-A/B/C原验收与历史证据，不拆一人一半，不仅复核EOCD补丁。源代码/测试逐行核验，结合PRD FR1000/1001/104、A06–08/G6和12.4/12.5，范围不缩减；正式格式/可信投影/生产lease/原子导入/真实App接线/双OS包内/真人/57P0/CI及正常合并/远端仍未完成。

round-1已双方各自真实终态，旧完整报告、所有意见和原owner处置在当前候选`docs/reviews/T10/round-1/`、`round-1-disposition.md`，现对称提供属于已完成历史；不能视为round-2 Pass。**禁止读取/接收/展示另一方round-2报告、摘要、结论、问题清单或对话**。本轮各全新独立任务；自己的报告结尾独立明确通过/不通过/无法验证，不给条件Pass或捏造ID。

新改动：EOCD实际成员数与声明一致才通过，不符ARCHIVE_SHAPE；原其他预算/角色/能力不变。66个定向Py、full check691TS/1118Py一次exit0、内审20项内存探针结果见internal-review.md，原工具stdout保留于独立审者会话；完整check原始日志另留validation/check-full.txt。render-probe输出out/t10-render-probe且3900B/26af内容未变；所有旧原件不覆盖。审者须自己评判与必要复现，不能以旧报告或数字抵当本轮核验。

旧native3896B/ad367与browser3900B/26af来自同一C的report源码不同标题输入、不同实际运行；它们未冒充本轮全新native。executed:null仅未观测到__t10xss哨兵，未测scriptContexts数量。attempt1容器已created、启动前CAP名称检查失败，StartedAt零，从未运行；旧backlog措辞保留仅作历史追溯。失败/missing仍保留。

审查运行可能产生官方.mimosa/hook-state等过程附加文件；逐路径/时间/hash与实际来源记录，不删原件或改verifier，不按目录名静默豁免，更不能因额外元数据自动声称受审源漂移。源/原输入/验收必须保持精确。scratch归档是不可执行证据；如要复跑在自己scratch解包/调整临时独立配置，不能把归档副本注入仓库源码/测试发现流。

当前桌面政策撤回静默/用户时段/CLI登录前置；必要GUI/原生互斥资源与root短协调，后台推理不占整段lease。不要无意义启动旧App e2e/stub或拿其冒充未接线服务。原未签运行票、自动审批拒绝、SQLite损坏HOLD等精确限制仍有效；无新增付费/密钥搬运/宽泛结束用户或别线进程权。

报告列实际身份/读过运行过内容/全部失败与首失败/每项优先级路径行触发影响证据建议/历史逐项关闭或未闭边界。当前P3延期不是已修复，不可略掉；如认为本阶段阻断，独立说明，不因旧报告措辞被迫Pass。最终指定MD保留完整报告。任务ID若模型不可见如实写未可见，由原owner关联真实创建/终态原件。
