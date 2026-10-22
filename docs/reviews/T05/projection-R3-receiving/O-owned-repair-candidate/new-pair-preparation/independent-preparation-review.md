# O15 全新同版双指定审查准备独立复核

2026-10-23，上海。**本次静态准备未发现阻断项，可由总控在既定调度范围派发新任务。** 这里只确认输入、scope、隔离和既有 setup 证据的准备状态；两应用实际任务尚未创建，actual task/settings/terminal 均未核，不能据本报告声称指定模型审查已启动、通过或到达终态。没有 GUI lease，也不签父/发布门。

## 审查对象及固定身份

完整 source 为 `b88be226501703f1d5365734dd0e56066bd1bffb`；过程为 `0f87f2c2a1fe5b8085176b530e473a7d51cea509`。实际两树分别为：

- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O15-zcode-review-b88be226`
- `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-O15-minimax-review-b88be226`

独立 Git 检查两树 HEAD 都是以上过程 ref，`git symbolic-ref -q HEAD` 返回 1、无输出，确认 detached。两树过程 tracked 元数据逐项等于固定过程 Git。未进入旧两棵外审树，未读取新 peer 报告、runtime、global 会话或模型任务内容。

共同 scope-contract = owner common-scope，1774B / SHA256 `21a9aae942880e3879c84ad2fe8597cc05dec7010bf6b46ba5242d2e966be28c`。launch-index 为 4835B / `dd5e472758b4266532ea29d1eb78ed09084077eed1d046dbb1b5390be3ab98ae`。

| 角色 | launch prompt bytes / SHA256 | manifest bytes / SHA256 |
| --- | --- | --- |
| zcode | 7094 / `0f17e4befa2775c9e0d704649419e862926ffd86f0716294ff7cfd732d5ca36d` | 95904 / `bebf5c075cce03bb619a984bbd6a23e3c944eed7aaecb4a550c0b37ed0e6c637` |
| minimax | 7142 / `81aa79c8f9f9ccb1ec69a1f2fe17569f984e37bb97192f79544f531b98d5fd18` | 95906 / `d81b138c295629f498c93ea53ed590da79e812579d79e2974384289189eccf5f` |

两 prompt 仅角色名、同角色 workspace 和指定设置不同；将这三项映射后全文相等，未见两方范围或验收分叉。要求设置分别 GLM-5.3/最高思考/yolo 与 MiniMax-M3.1-Flash/xhigh/bypassPermissions；这些是待实际任务读回的要求值，index/map 的实际字段正确保留 null。

## 全范围和共同历史输入

独立解析原 149 工程清单及新 150 清单，路径集合精确关系为原 149 全保留 + 唯一 `.prettierignore`，没有按 delta 减项。150 路径全包含于两方显式 450 保护件；完整 source tracked-tree 的 1246 条 UTF8 path/mode/type/blob/bytes 与固定 source Git `ls-tree -r -l -z` 逐项相同；过程 Git 为 1262 条。数字和 metadata 只证明材料范围与身份，不代表指定模型已经读过。

五项旧阅读缺口在有效 prompt 中明确要求新任务全文补齐，不能用 selected lines、统计、旧报告或 hash 当读全。本次核其固定 bytes/SHA、实际存在及行数：PRD 1255 行、allocation-integration 159 行、allocation-restore 249 行、package-lock 6423 行、uv.lock 240 行，均与 next-pair-five-full-read-requirements 相等。本准备审查没有冒称已替两指定模型完成五项内容审查。

原 frozen-original-prompt 在 zcode 为 6426B、minimax 为 6444B，均逐字等于原 review-packages/O 对应 prompt 和固定过程 Git。新 prompt 明确保存原完整验收，并将旧 owner 绝对路径/source/process 作为历史定位映射到本方相对路径及新固定候选。旧禁止所有 oracle 执行的文字，由当前有效映射精确补充为本方两条正常命令，未放宽其余物理研究/actual/GUI 边界。

共同原件包含原始 PRD/FR/附录、original-acceptance annex、backlog、coverage、source-authoring、完整 authoring/fixture/tools/history、六历史工程各自候选身份，以及旧双方意见和首错。独立确认原 M 最终完整 15 意见原件 44941B / SHA256 `9921ffe20f68b1bbf5c7938fa7d45c9b0059cd9c8ed5b0a4afcb5a6e23852df7`、12978B 最小修复计划及完整 triage matrix 可在固定过程 context 中读取且 bytes=Git；不只是给新模型 owner 处置摘要。450 不是全部历史文本的字节保护声明，完整过程 Git 和原 scope 的历史 context 继续要求阅读。

all-15-owned-disposition 有完整 15 行，均 externalReviewerOpinionClosed=false；原首发现/P2 修复、build01/02、style 首错、fullcheck01/02、native 初败与同锁修复、raw whitespace、77 档案诊断含 15 B023 在有效 scope 内，未作为修复后“失效”意见删除。417/280specified/137pending、26 allocation pending、whole=false 及父门未关，均保留。

## 输入字节及 setup 原始记录

不重新运行 setup/helper。独立读取每角色 manifest 声明的 450 已知件与 10 launch 输入，校验精确路径、重复项、bytes/SHA，并对 450 件计算 Git blob 身份与固定过程 tree 比对；两方 450 列表及内容完全相同。10 launch 输入和 manifest 本身均与 owner 副本及实际新树副本相等。未读受限 actual ZIP；显式列表没有将 ZIP/runtime 原件变成已消费输入。

两方保存的实际 setup raw invocation/result/stdout/stderr 与 owner副本逐字相等；environment 和 preflight 两步的 result 都是 exit0。环境 argv 为 `/opt/homebrew/bin/python3.12 -B -m venv --without-pip <本方>/.venv`；校验 argv 为本方 `.venv/bin/python -B <本方launch>/verify-input.py --phase setup`，cwd 是各自树，TMPDIR 是本方 scratch，PYTHONDONTWRITEBYTECODE=1。两份快照记录解释器均为各自 `.venv/bin/python`、3.12.14；未把 without-pip venv 创建称作依赖安装或产品执行，也未用 owner 可变 venv 给指定树背书。

| setup 快照 | bytes | SHA256 |
| --- | ---: | --- |
| zcode preflight-setup.json | 3423 | `d94984af5049e1a15e82cd52ec8fcefa4a2bd9165bf3e60631caead9789eec3e` |
| minimax preflight-setup.json | 3427 | `bd3ccb927b5a8b93a6f19954dbd282eb8147f9b64117cf19c38cd6f113a66788` |

快照准确分开 450 protected bytes、10 launch inputs、1262 tracked metadata；未知 own raw/scratch 自动件仍只 path/lstat，contentOpenedOrHashed=false；`.git` 和已声明本方 `.venv` 作为 administrative/environment roots 明示省略。它们没有声称整个文件系统字节冻结。未知记录非空不是失败被清除：本来就只记录其存在，未删除、hash 或归因为别方内容。

## 新 helper、执行与政策边界

新 helper 5497B / SHA256 `a8d43c5b48e1e0f8be6fc53d2820b6d3395b719699db6d702b49dbd6d295a9e9`，template、两 role 和实际两 launch 副本一致。全文/AST 静态复核确认：只读取显式 manifest/protected/launch 文件，拒绝声明路径绝对/越界和路径祖先 symlink；核本方 workspace/HEAD/3.12 解释器，既有观察输出拒绝覆盖；unknown分支仅 lstat，os.walk 不跟随 symlink，未打开其内容；不调用产品/oracle/旧 B023 helper。HEAD/source和受保护字节核查不提升为未保护全部 tracked 内容/全 FS 冻结保证。本次另行 Git 核准了实际 detached 状态，不将 helper 的 HEAD 值检查误称分支检测。

helper 首轮 2 个 E501 已在 style 记录说明，后续 targeted lint/format 0；本审只核文本/AST及原流，没有重跑，也不把末次 formatter 0 当首轮 lint0。

历史 AGENTS 1056B、SHA256 `1b3c02916e9bab79f463a61f2818846f01e849014b70251b37c112377443a6fb` 保持实际树 Git 原件；stage 当前 overlay 15147B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` 和本用户七条工作偏好另冻结提供。有效 prompt 明确当前与历史身份、精确 NoGoal 和只读职责，覆盖共同指南泛 Goal/宽泛运行授权；没有声称树内 AGENTS 已被覆盖。

必要正常 O 复验仅限各自本方准确 3.12 解释器的 self-test 与 builder `--check`；禁止裸 build、系统3.9、安装和跨树环境。静态 observe helper 是单独显式许可，只写本方一次性快照，不扩为第三条产品/O业务命令。报告/本方 scratch/raw 为唯一写面，冻结输入只读；peer 新报告/runtime/global session 禁读，受限三 actual ZIP 只保 manifest/缺口。旧 fullcheck03=0 是 owner 精确来源/环境结果，不替新指定模型签实际执行，亦未把两应用待核设置写成已执行值。

本次独立方法仅 Git/JSON/hash/AST/文本和既有 raw 核验，没有 setup/observe 重跑、产品、原 oracle、模型、GUI、安装、网络或 DB。唯一新写面为本报告。准备状态通过不代表新完整审查本身通过；实际创建后的 task/settings/workspace/权限、完整已读覆盖、运行边界、终态及逐意见处置仍由原指定双方各自给出，总控全文验收。

## 根指示实际 AGENTS policy overlay 后继定向复核（2026-10-23）

**后继准备状态限定静态 Pass，无新增阻断。** 上文是政策调整前 8553B / SHA256 `10c2c0f4e91c8d122efa14f8557378fd755df1f3b3310c5dc41470dde87d2734` 初版的真实记录；其中“实际树 AGENTS 保持1056”的时点描述由本节后继状态取代，不再作为当前派发前提。根明确指示已落实为两实际树的 15147B current policy overlay，source/过程候选没有重建或改写。

初版全部 47 件（含本报告初版、两方完整初输入及 first setup 流）以 `initial-preparation-before-policy-overlay.tar.gz` 保留，109979B / SHA256 `f343fc791efe10352ab3dd65f343f84c6604cab3f7e9c830c0e68f1e314f3e47`。本次独立只在内存核该已声明 archive 的内容/成员，没有解包写文件：47 个文件，初报告精确8553/hash同上；两 role 的 preflight-setup.json 与 archive first 原件仍逐字相等，未覆盖初次流水。

当前两实际树的 `AGENTS.md` 都为 15147B / SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，逐字等于各自冻结 guidance/AGENTS-stage-current.md。Git0f87 历史原件仍为1056B / `1b3c02916e9bab79f463a61f2818846f01e849014b70251b37c112377443a6fb`、blob `f3876f6690b11ae58f633d1bcb96db05a429d58b`，另在 historicalGitAGENTS 明确 pin。独立 Git 读回两树仍 detached `0f87f2c2a1fe5b8085176b530e473a7d51cea509`，index 空，tracked 未暂存改动精确只 `AGENTS.md`。这是授权操作政策覆盖，不称受审 source150 或 process Git 漂移。

原450 protectedFiles逐项与 archive 初版相等，原本不含 AGENTS；新 manifest 的 policyOverlays 单独且唯一为当前 AGENTS 行，不把15147混作450的历史Git内容。基于前轮完整450字节/Git核查、本轮列表不变与两树除AGENTS外无tracked变化，本次没有重复遍历450文件。新10 launchInputs和manifest本身则全部重核 bytes/SHA/实际树与owner副本关系；frozen-original全文和五份 guidance 与 archive 逐字不变。

共同scope当前2476B / SHA256 `757682e1a0e3d389cc7cc4b89c4ea3a7ba6c38623ad66c4c01771cb4cd6e86f5`。初版所有scope字段逐项不变，仅增current/historical policy及环境边界。150=原149+.prettierignore、1246source/1262process metadata、五项完整阅读缺口、全部15历史意见/失败、137/26 falsewhole、两条准确本方3.12普通O命令和禁止peer/global/actualZIP边界均未缩减。

| 角色 | 当前 prompt bytes / SHA256 | 当前 manifest bytes / SHA256 |
| --- | --- | --- |
| zcode | 7231 / `1c51fb3284ed83158e304d689cbe686154d64f6c207926939dbda706d3f9f94f` | 96353 / `83f1d24ac54e05348a38ddaf4ca043d93bd56c382448ea88ab900a7ead4f288e` |
| minimax | 7279 / `c31f1b5d44bb008becdadb21b4ea156058548c809cbcbf9d5db80e47e6629ddd` | 96355 / `43738f6d6412978d210c450ffa90e04269c1202eab2a13dc7ce7a4f73a25b174` |

helper后继6748B / SHA256 `3d016963da274880a5bbb9532600fbbbf7f793c0b1206ca08cdd86177baded48`；静态diff/AST确认只增加独立policyOverlays的读取校验、历史Git AGENTS bytes/SHA核对、overlay paths须精确为AGENTS、未暂存改动须精确为AGENTS及index为空的守卫；新增 `setup-policy-overlay` phase和对应历史/current记录字段，原setup不覆盖。未知分支仍仅lstat、os.walk不follow symlink，`.git/.venv`仍明确省略，不读取unknown内容，不宣称全FS字节冻结。

两方新 phase `setup-policy-overlay` 原 result 均实际0，准确解释器仍各自3.12.14、cwd/TMPDIR仍在本方；原invocation/result/stdout/stderr与实际两launch镜像逐字相同。新快照分别 zcode5240B / `03b71baa5a58511c81c05415bd51e2f912ce3ec2a105279db6a7049d889c020a`，minimax5244B / `370149681f64e0da5427aaf61dc69383944e8711c62b84507a0185d70bc53934`；其中450、10和唯一1个overlay分列，onlyUnstagedTrackedChange标记与本次独立Git事实一致。

有效prompt/map现在明确实际AGENTS15147、历史Git1056的双身份；共同开发指南的泛Goal/运行授权仍被当前NoGoal和只读窗口限定。venv明确只是without-pip的stdlib运行准备，非全repo依赖齐备；不让指定reviewer安装或机械复跑完整check。现有fullcheck03结果只按旧精确候选/环境证据引用。

本次仍只做静态archive/JSON/AST/hash/Git/text复核，没有运行setup/observe/oracle/product/新模型/GUI/网络/安装。本轮index/map的actualTask/settings/terminal继续null；model0只表示本套setup没有创建新指定模型任务，不是对全局runtime或其他聊天的审计。本节只给精确当前准备范围的静态Pass，不签实际指定模型结果、完整阅读覆盖、终态或父/发布门。
