# T07 完整工程外审：静态调用预检与执行边界

本文件是新派发的操作补充，不改B→f9产品/测试/验收、旧round-1正文或manifest。当前只做setup和静态准备，没有运行下表产品检查。正式审者在root预检并短时创建各自任务后，可按必要性运行普通对应检查，不机械重跑无变化历史。

## 正常验证的实际调用

| 命令/入口                                                                                      | 固定源码中的实际调用和副作用                                                                                                                                                                             | 本次派发边界                                                                                                                                                                                                                                                                                                |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `npm run check`                                                                                | 根package.json依次lint、format:check、typecheck、vitest、electron-vite build、ruff check/format-check、pytest                                                                                            | 审者必要时可跑完整正常检查；记录每段退出码及首错，不能把setup当check通过。无修改型format、HMR、Electron启动或打包产物运行                                                                                                                                                                                   |
| `npm run lint` / `npm run format:check` / `npm run typecheck`                                  | eslint读取工程；prettier检查；contracts/unit/desktop三个tsc检查。原 `.prettierignore` 忽略旧归档docs/reviews                                                                                             | 可执行；新报告/metadata造成状态或检查差异须如实记录，不新增ignore、删metadata或改源码求绿。新派发文档另显式格式检查，冻结原件不格式化                                                                                                                                                                       |
| `npm test` / `npx --no-install vitest run tests/unit/t07-scenario.test.ts`                     | `vitest.config.mts`包含整个tests/unit。`task-runtime.test.ts`真实spawn本树`.venv` coordinator/worker和临时SQLite；engine-environment真实Node子进程。window/native-driver相关单测使用mock，不启动Electron | 允许必要原正常单测及受控worker回归，不能因为名称含native/child/SQLite就一概禁止。不得设置ROOT_SOURCE_PATH指向其他树，不能改测试或读取peer                                                                                                                                                                   |
| `uv run --frozen pytest` / 两个T07专项pytest                                                   | 根pyproject的testpaths是packages/engine/tests。原套件包含Store/Job临时SQLite、事务/取消/READONLY、受控异常退出、owner PID/bootstrap与runtime边界；T07持久化专项44项含10个真实os._exit子进程              | 允许固定原套件中这些受控回归。只用本树venv/已批准固定源码和自己新建临时DB，原测试的精确自有PID清理/临时目录回收可按原逻辑执行。不得借此新增物理资源、损坏研究或新native/caller/producer票                                                                                                                   |
| `npm run build`                                                                                | desktop workspace仅`electron-vite build`，写本树out，未启动Electron                                                                                                                                      | 必要时允许普通构建，保持输出与日志可归因；不自动运行产物                                                                                                                                                                                                                                                    |
| `npm run verify:sources`                                                                       | 仅运行scripts/verify-sources.mjs，对归档源做本地hash校验                                                                                                                                                 | 必要时允许，不改归档源                                                                                                                                                                                                                                                                                      |
| 原 `evidence/render-probe.mjs`                                                                 | 原脚本读本树页面与fixture，临时Vite构建、sandbox headless Chromium，再写`docs/reviews/T07/evidence/ui-probe.json`及PNG；finally回收自己`.t07-ui-*`scratch                                                | **禁止在固定review checkout原位执行，避免覆盖旧证据。** 如审者确需补验，应先在其独占scratch建立完整固定reviewHead的Git文件副本，逐项核来源/输入身份，以该副本为cwd调用原脚本；产物只落副本。使用自己环境及已有可用Chromium，不修改候选脚本、不改sandbox。保留副本清单和原始新输出；不能把合成页面当正式接线 |
| dev/HMR、`test:e2e`、`engine:build`、`package:dir`、新native/caller/producer、真实业务模型/API | 涉及窗口、HMR写源码、安装/打包/产物、或其他单独运行票                                                                                                                                                    | 本次普通工程审查不授权新增这些运行；发现实际必要缺口交owner/root精确调度，不把桌面静默、用户时段或CLI登录当当前前置。桌面政策撤回不解除原明确HOLD或自动审批拒绝                                                                                                                                             |

受控原套件可能会使用ctypes/原生进程身份观察或SQLite临时损坏/迁移fixture，这不是新增ABI/loader/drain或物理资源实验许可。不得泛禁原child/SQLite套件，也不得接触正式业务库、其他树运行库、未批变化源码或扩大已拒绝命令；遇实际自动审批拒绝须保留原理由，不变换包装绕过。

## 实际环境隔离和取证

每个审者只用其自身review根作为应用workspace/cwd。node_modules与.venv位于各自Git树，npm/uv cache、scratch、TMPDIR、pytest basetemp、raw、metadata位于其独占`.runtime`旁目录。没有共享可变env、venv、DB、报告或scratch；系统Node/uv/Python基础解释器和Git对象是只读工具/对象，不是共享运行状态。

setup只允许按原锁执行`uv sync --frozen --no-python-downloads`及`npm ci --ignore-scripts --no-audit --fund=false`，逐命令留完整stdout/stderr、起止时间和退出码。npm lifecycle未执行，不据此声称Electron二进制或产品测试已验。UV缓存、npm缓存与TMPDIR均明确归本角色。没有在setup中运行产品。

实际运行普通检查时，将TMPDIR/UV_CACHE_DIR/UV_PROJECT_ENVIRONMENT/npm cache/RUFF_CACHE_DIR指向本角色路径；清除ROOT_SOURCE_PATH、PYTHONPATH、ONTOLEARN_TEST_ENGINE、ONTOLEARN_DB_PATH等跨树或业务库覆盖。pytest如显式basetemp必须使用本角色新的唯一子目录，不能重复指定已有原件目录。记录每次实际命令、环境中非敏感路径、退出码、原始输出hash与源码前后身份。不得打印环境凭据或读取认证文件。

审者可写自己的最终报告和独占sidecar下检查/取证/metadata材料，允许原正常检查生成本树out/cache；实现、测试、fixture、验收、锁、配置、旧证据及旧输入保持只读。应用确实生成的本树metadata按路径/大小/时间记录增长，保留原状态；不清理、不新增ignore掩盖，也不把预期metadata dirty当产品变更。敏感凭据不读取或复制。AGENTS由阶段主聊天唯一传播，保护M不stage，setup owner不代改。

## 独立性和完整审查门

本轮完整范围仍为B→f9全部25路径、14实现/测试/fixture及全部原验收、历史首错与IR-01～05发现/关闭；没有缩为最新delta、source-only或单项投影。P前6个技术组成在同一个完整S1任务内审，真实T05/T06、T01/I04生命周期、App/bridge、完整E5、T10跨设备与两OS/真人/发布缺口照实记录；这些父缺口不阻止对现有完整工程给出独立结论。

严禁peer本轮报告、状态、任务流、metadata的读取或发现性枚举：不扫其他worktree、controller实时队列、其他应用任务/账号或全session历史。旧原始内审消息只读本树封存9条，不跟随source索引到正在增长的原session。Git只读本任务指定base/product/reviewHead与本树状态，不做其他worktree/refs发现。两模型只用各自root和输入，不互传本轮意见。

模型、思考和权限均是待逐任务读回的要求，不预填实际Pass或实际任务设置。需要真实任务ID/正文受理/完整终态、全文报告、命令和未验项、所有意见处置及前后冻结身份；后续push/PR、CI、正常合并、远端和完整父功能门均保留。setup/普通文档独审不是指定双审。

## 准备首错记录

初次只读枚举误试了不存在的`uv.toml`与`vitest.config.ts`，相应cat命令非零，未执行任何产品。随后依据文件清单读取真实根`pyproject.toml`、`vitest.config.mts`、`eslint.config.mjs`及`.python-version`，完成上述调用预检。没有因首错修改产品或丢弃历史证据。
