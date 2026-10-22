# T07 两树完整派发准备

本次仅setup与静态准备，尚无T07指定任务、任务级设置回执、产品检查或指定Pass。原T07 Goal、产品/测试f9、旧round-1输入/manifest保持。root预检后再给短时创建/设置/读回GUI租约；准备时T01持当前前台lease，后台推理不占整个应用。

| 角色    | 实际应用workspace                                                            | 固定reviewHead                             | 完整新输入                                                                                          |
| ------- | ---------------------------------------------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| ZCode   | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-zcode-review-f9a1157`   | `24f3703ecf4fce75e0d0375f7291ed928f083c41` | 本目录`zcode-full-input.txt`，同字节副本在该树`docs/reviews/T07/dispatch-20261022/full-input.txt`   |
| MiniMax | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-f9a1157` | `24f3703ecf4fce75e0d0375f7291ed928f083c41` | 本目录`minimax-full-input.txt`，同字节副本在该树`docs/reviews/T07/dispatch-20261022/full-input.txt` |

受审base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → 产品/测试 `f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`。完整25路径/14实现测试fixture，非末delta或source-only子范围。历史首错、IR-01～05、9原始独审final和全部75归档成员保持；原验收和全部父缺口透传。每个新正文为当前完整补充＋旧完整prompt精确原字节suffix；`*-input-manifest.json`给出前缀长度、suffix offset、整体/前缀/原件hash。`.txt`是精确派发文本，不做格式化。

## 实际完成的准备

- 每树832个tracked文件逐项核物理字节，831项等固定reviewHead；唯一差异是阶段主聊天传播的当前AGENTS `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，M保护、不stage。14项产品/测试/fixture全部仍等f9。全源码清单是`full-git-files-{zcode,minimax}.json`，各树只得到自己的`current-inputs/full-git-files.json`。
- 每树`node_modules`和`.venv`为独立实际目录，editable Python包绑定本树packages/engine，workspace包link只指本树。sidecar绝对路径为对应workspace后加`.runtime`，分设raw/setup、raw/validation、scratch、tmp、metadata、reports和各cache/pytest目录。两方不共享可变env、DB或输出。
- 各自`uv sync --frozen --no-python-downloads`与`npm ci --ignore-scripts --no-audit --fund=false`退出0；四份完整原始日志在各sidecar保留，同字节副本在本目录`setup-*.txt`。`setup-results.json`记录命令/路径/起止/退出码/hash。npm旧包deprecated警告和版本notice保留，没有更新锁或全局工具。
- setup仅安装原锁依赖，uv的本地editable构建属于环境准备；没有运行产品、测试、构建验收、headless、Electron、外部模型、GUI、登录、凭据读取或付费。没有将忽略npm生命周期的安装冒称Electron运行环境通过。
- setup前AGENTS曾为固定基线版；随后由stage主聊天正常传播de15，当前各树metadata/setup-after.json记录保护M及新hash。setup owner没有代改AGENTS。

## 执行和独立性

`execution-boundaries.md`已静态检查根package scripts、vitest.config.mts、Python testpaths及受控worker/SQLite调用。正式审者可按必要性做普通对应检查/受控测试worker回归，不机械复跑历史；不得泛禁child/SQLite原suite，也不得扩张物理资源研究、被拒命令、新native/caller/producer或付费API。原headless脚本写回旧证据，不能原位跑；若确需补验，须在自己的完整固定Git副本中按原脚本执行并保留新产物。

每方只收自己的完整正文、manifest与current-inputs，应用workspace/cwd必须选自己的实际根。严禁peer本轮报告/状态/metadata发现读取，不扫描其他worktree/controller队列/全session；旧sourceSession仅作为封存来源索引。自己的metadata增长保留并记录，不删、不增加ignore求绿。普通检查输出/受控原测试回收自身临时进程和目录按明确边界执行。

当前桌面政策已撤回静默/用户时段/CLI登录前置；旧正文的历史操作限制由新前缀明确更新。仍须root短时租约和真实逐任务模型/思考/权限读回，指定双方同版独立完整审查、真实终态/全文报告/所有意见、必要CI/两OS/真人/远端门全部保留。父领域/App/Job/跨设备未完成如实记录，不因此拒绝准备已有完整工程审。

## 原件、核验与状态边界

`roots-and-isolation.json`保留最初setup快照；当前精确输入、源字节和环境事实以`dispatch-manifest.json`、每方input-manifest及各树metadata/setup-after.json为准。策略快照在guidance/，后续实际派发前再由owner核当前有效政策/输入，不让审者去发现peer或队列。全量积压过程15dcbb1的只读副本在各树current-inputs中，不改变固定产品。

本次需要限定独立准备审查，原创报告追加在本目录`preparation-audit.md`。该普通审计只核准备物，不替代ZCode/MiniMax审查或产品运行。当前文件和manifest中的未创建/未读回/未运行状态不可预填通过。

当前限定准备独审已完成：未发现阻断P1/P2，仅通过本次静态准备范围。原创报告preparation-audit.md，格式前精确原件preparation-audit.original.txt；两份身份及受审manifest身份见preparation-receipt.json。dispatch-manifest的pending字段保留准备时快照，不改写其受审字节；本回执补充实际过程结果，仍无指定任务/产品Pass。
