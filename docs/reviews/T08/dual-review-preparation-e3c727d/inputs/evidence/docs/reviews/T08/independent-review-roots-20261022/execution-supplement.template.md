# 本轮执行补充：物理独立工作树与正常验证授权

以下为总控2026-10-22最新明确授权补充。前缀完整旧prompt逐字保留，是完整工程/历史/原验收输入；旧prompt中的原开发树路径、旧报告路径、只准备不允许普通检查的限制由本补充精确替换。不是source-only新S1，也不是只审delta。全部FR/A/Q9、11.3/12.2、原附录和57P0门保持。

## 真实身份和同一完整工程

本任务角色 {{ROLE}}，应用实际workspace必须是`{{REVIEW_ROOT}}`；实际Git为detached HEAD `5b64bfea538b638310cd3ce79e595c3b482e003d`。原开发branch `feature/weekly-t08-agent-model`仅为历史，不切换/新建branch，不初始化Git，不cherry-pick/提交/推送。base仍`5f910b52c69d86a1076b2032e5d3c63e715947f3`，product仍`93516fa8455cf4b195cbfb699aa7a6652d428b6f`，reviewHead含原完整准备包。此工作树由root真实创建，注册清单SHA见本轮dispatch-manifest；保护AGENTS应为de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4，保持M、不stage，不以它与旧GitAGENTS不同认定产品漂移。

必须实质审完整codec/provider数据层、session、receipt、sidebar、全部评估及历史失败/关闭；含旧包全部25源码/测试/fixture、44产品差异、828产品树，不只看新补充。旧包在本树`docs/reviews/T08/dual-review-preparation-93516fa/`，旧input-manifest SHA `33deedd2aaeb18852d513bef4d46ab047a27ded380d7fff9ef03e3eb9e9ba317`不改。源码读取以本树固定Git对象/已有快照为准，旧manifest里原开发树地址只为历史来源；不要去原开发树找本轮运行状态。

源码/快照完整性见本树`docs/reviews/T08/review-runtime/metadata/source-git-bytes.json`，不是测试通过证明。root要求缺真实API也审已有完整工程，不能以无法预判Pass而拒绝读代码；也不能把纯代码局部结论当完整功能Pass。

## 独占路径与盲审

- node_modules：`{{REVIEW_ROOT}}/node_modules`；Python环境：`{{REVIEW_ROOT}}/.venv`，已按原锁setup；不得复制、软链或复用其他checkout的可变环境。
- 本轮scratch：`{{REVIEW_ROOT}}/docs/reviews/T08/review-runtime/scratch/`。每次验证新建唯一run编号，TMPDIR使用该run的tmp，pytest basetemp使用该run的pytest；旧raw/失败/metadata不删。不要把Python可执行文件resolve到venv外，用`.venv/bin/python`词法入口。
- raw：`{{REVIEW_ROOT}}/docs/reviews/T08/review-runtime/raw/`，使用.txt；metadata：`{{REVIEW_ROOT}}/docs/reviews/T08/review-runtime/metadata/`，记录任务/session/turn、真实模型/思考/权限、具体命令、cwd、exit及raw摘要，不用预期设置冒充读回。
- 唯一报告：`{{REVIEW_ROOT}}/docs/reviews/T08/review-runtime/reports/{{REPORT_NAME}}`。setup日志和setup.json仅为环境结果，不是审查已启动或产品通过。报告写本树，不能写旧prompt的原开发树/另一角色路径。
- 禁止读取、搜索、探测或枚举另一模型本轮报告、raw、状态、metadata、任务数据库/session/stream；不扫描父.worktrees，不git worktree list、不发现peer文件，不向另一模型转发本轮意见。冻结旧Codex内审1–8是双方共用历史输入，不属于peer本轮意见。
- app可能新增workspace metadata。逐项记录自身status/文件增长及来源，不删除、不追加ignore、不重置环境或改AGENTS以求Git clean。只核对源码等固定字节；已存在node_modules/.venv等ignore是原配置，不新增规则掩盖审查metadata。正常测试原有自有临时fixture收尾保持，不外推为删除审查证据的授权。

## 允许的必要普通验证（本补充是审者执行边界；setup owner尚未执行产品）

每条命令cwd必须是本树。先核对setup及锁/源码，再按代码疑点选择必要对应检查；已读历史日志不机械重跑，无变化同一成功命令不重复。必要检查的新stdout/stderr、失败和exit保留自己的raw/metadata，不猜测通过。

允许原锁下现有命令：`npm run check`及其原拆项`npm run lint`、`npm run format:check`、`npm run typecheck`、`npm test`、`npm run build`、`npm run engine:check`；必要时`npm run verify:sources`。定向可用已装的`./node_modules/.bin/vitest run tests/unit/<现存文件>.test.ts`或`uv run --frozen pytest packages/engine/tests/<现存文件>.py`，不得自动下载临时runner或新造测试。Ruff仅check与format --check，不用写入format命令。全check确有必要时可做一次，不因工程还缺provider/domain而禁整个原suite。

运行前明确取消可能指向其他源码/包的`ROOT_SOURCE_PATH`、`ONTOLEARN_TEST_ENGINE`及`PYTHONPATH`，不读取/打印其值；显式令UV_PROJECT_ENVIRONMENT与VIRTUAL_ENV指向本树.venv，TMPDIR与PYTEST_ADDOPTS只指本run临时目录。不要输出环境全集、.env或凭据。venv的editable .pth和direct_url.json必须指向本树packages/engine；npm工作区contract引用也指本树，setup已记录。可用shell env -u这些三个名称搭配上述本树资源路径启动原命令；不更改产品或测试来实现隔离。

原正常回归中以下全部允许，不能泛禁child/SQLite/native导致原suite无法执行：

1. `tests/unit/task-runtime.test.ts`的本树Python coordinator/worker、stdio、临时SQLite、受控test.read/test.rounds/test.atomic故障、终止确证属于本测试的精确PID与恢复；这些test.*始终是基础设施回归，不是已发布领域能力。
2. `tests/unit/t08-fixed-input.test.ts`用本树.venv Python -I执行固定finite-case RDFLib/CSV probe（原10秒/1MiB界限），不发真实provider请求。
3. 原`packages/engine/tests`的事务/迁移、PRAGMA max_page_count数据库满、逻辑异常、commit前中后故障/子进程退出、worker owner等既有受控临时库套件；原memory guard中的受控子进程/平台OS调用属于此已有suite。只操作自有tmp_path与确证自有PID，不宽泛kill用户或其他任务。
4. 桌面build是electron-vite编译，不是启动Electron。原生成out/cache在各自树中；不得因为有Node/Python子进程就说违反当前授权，也不得由此宣称真实native UI或两OS通过。

## 不从普通检查推导的权限

不调用DeepSeek/付费API，不读/搬key、.env或secret，不开户/充值；实际provider、endpoint/principal授权、费用上限和正式质量评估仍未证明。不修改实现、测试、配置、依赖/锁、原prompt/manifest或旧报告；发现问题列明，留原owner按唯一写面修后新验证/双方新同版审。

`npm run dev`、`npm run test:e2e`（含install-electron与Electron启动）、engine:build/PyInstaller、package:dir、启动产物/凭据/native UI验收不在这份普通检查票内，需root另签精确运行资源；这不是恢复静默桌面偏好。冻结旧suite已包含的worker生命周期/OS采样允许，不可一概禁native字样；新增未签native loader/caller/producer、ABI/位置供应、被拒物理资源分析及SQLite损坏HOLD/whole-H研究均不得借原suite开启。不得扩大输入域、制造额外磁盘/WAL/RSS压力研究或用篡改DB绕过HOLD。自动审批已拒绝的动作不能重试绕过。

桌面仅创建/设置/核验按root短lease串行；后台推理不独占整应用。本准备未获得GUI lease、未创建模型任务；实际派发的owner再读回模型{{MODEL}}、思考{{EFFORT}}、权限{{PERMISSION}}和精确workspace。不能读取peer队列来抢资源。

## 完整结论与父门

真实I06安全传输/最终字段授权/最小日志、T01真人Diff确认/事务/撤销恢复、领域/App挂载、真实API主体与消费上限、实际模型正式模式/零伪造质量、两OS和真人均无本线完整验收。请完成已有全部代码实质审查并给NotPass/无法完成验证或有实际证据支持的完整结论；关键验收缺失不得Pass，不能为入队缩FR/A/Q9/11.3/12.2。明确区分静态检查无问题、受控worker/库测试、真实领域/平台/生产。全部缺口与可修问题均定位，不只回复等依赖。

报告记录base/product/reviewHead/实际detached状态、旧完整提示前缀SHA、新完整派发正文SHA、旧input-manifest与本dispatch-manifest SHA、真实设置和实际运行命令/退出/raw，历史1–8问题逐项关闭。真实task/session/turn未创建前保持未知；读回全文报告及终态后才有本轮结论。CI/两OS/真人/远端/57P0发布门不因准备/局部检查通过而删除，原Goal不重建或预填完成。

## 当前完整操作政策（逐字快照）
