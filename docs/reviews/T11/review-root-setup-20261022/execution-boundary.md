# 审查执行边界：先静态调用审计，setup未运行产品

原完整工具范围与acceptance不变，全部25个变更、两collector及历史原件均在审查内。base为5f910b52c69d86a1076b2032e5d3c63e715947f3，product为7d28fdb27c0aac39ed7df1f9fd5fa0f127b5d9f4，review HEAD为b6e57a0534c94316dd07c3a87b4b8931d5a39501。两个review根为真实独立detached Git checkout；各自node_modules/.venv/tmp/raw/report/metadata独占。当前仅setup/提示准备，未派审，无GUI租约。

## 原正常验证的静态调用链

| 入口                           | 实际源码调用与边界                                                                                                                                                                                                                                                                     |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| npm run check                  | package.json依次lint、format:check、typecheck、test、build、engine:check；不含e2e、打包、collector或模型API                                                                                                                                                                            |
| npm run lint / format:check    | eslint配置忽略release，prettier忽略release/reviews/原始归档等；成功不证明这些路径被检查，必要时使用原显式lint/format入口                                                                                                                                                               |
| typecheck                      | contracts tsc、unit tsc、desktop tsc；tsconfig.unit.json包含unit测试及其导入的verify.ts                                                                                                                                                                                                |
| npm test                       | vitest.config.mts仅tests/unit/**/*.test.ts。原suite有受控Node/Python子进程、stdio、tmp SQLite；不可一概禁child/SQLite                                                                                                                                                                  |
| T11固定专项                    | T11_FIXED_BASELINE_PROBE=1 npx vitest run tests/unit/t11-release.test.ts。fixture使用TMPDIR内mkdtemp，读取固定873 Git对象、核17文件hash，spawnSync调用本树Node CLI；不打开产品、不发模型API。actual仍oracle构造，不是领域运行                                                          |
| npm run build                  | apps/desktop package调用electron-vite build，配置构建main/preload/renderer并注入生产CSP；serve分支才配置dev server。不是electron-vite dev，不启动Electron产品                                                                                                                          |
| engine:check                   | uv run --frozen ruff check/format --check，再uv run --frozen pytest；root pyproject指定packages/engine/tests。原test_resident_runtime/test_worker_parent/test_i04_round_faults等使用自有temp DB和实际受控Python coordinator/worker、精确owned PID清理；是原suite，不是另造物理资源研究 |
| npm run verify:sources         | scripts/verify-sources.mjs只读source-manifest列出文件并sha256核对，无产品启动                                                                                                                                                                                                          |
| release显式检查                | 原acceptance列npx eslint --no-ignore verify.ts/CLI、prettier --ignore-path /dev/null指定release文件、bash -n Mac collector；Windows collector当前仍仅静态，无Windows真实执行                                                                                                           |
| e2e / package:dir / collectors | 不在本轮普通check内。test:e2e会install-electron+Playwright；package:dir会build-engine/PyInstaller和builder；collector会codesign/spctl/stapler或Authenticode实际系统验证。当前没有扩大这些运行票，不能自动执行来填父平台缺口                                                            |

此次setup只执行每根npm ci --ignore-scripts --no-audit --no-fund及uv sync --frozen，均exit0；保留各自raw安装日志及hash。Node24.15.0/npm11.12.1/uv0.11.12为实际工具版本。未运行check、专项、pytest、build、collector、e2e/native或模型。未执行Electron安装脚本，不自动补跑postinstall。

## 实际派审后的允许与限制

指定审者在root短租约完成真实应用workspace/模型/权限读回并派发后，可按审查必要性运行对应原普通检查和受控测试worker回归；不机械重跑无变化历史。允许既有suite子进程、独立临时SQLite、原受控PID生命周期/故障回归及既有符号/模拟边界测试，不因关键词child/SQLite/native将整suite判禁。

不能扩展被拒物理资源研究、全新native caller/producer票、新资源压力/内存研究、外部SQLite损坏HOLD的特定探针或真实用户DB。不能以“原suite”绕过另有明确HOLD的精确操作；若某原调用与特定HOLD冲突，报告准确测试/调用并由root分辨，不能默默skip、改断言或禁整suite来取Pass。无新增API消费/付费/密钥读取/搬运/签名/公证/分发授权。不得关闭sandbox或hang monitor、隐藏/stub原生结果冒充通过。

每次命令仅在自己review根，TMPDIR/TMP/TEMP为自己.t11-review-runtime/tmp；每次运行日志用唯一文件名留在自己raw，pytest基目录若显式指定须唯一，不能覆盖旧失败证据。输出/模型报告/任务ID/权限读回及app生成metadata只进自己根。保留git status的真实metadata生长；不得删文件或加ignore求绿。公共命令因metadata格式等失败须分别报告原命令、真实失败和来源，不通过cleanup/exclude改写成全仓通过。

不读取peer本轮报告、状态、metadata或父目录扫描发现；审者无需读总控队列/其他worktree，历史25路径与已有报告均已在自己Git树。设置两个独立应用workspace为各自精确物理根，不选原开发树。只有创建/核验短时前台内部串行；不能将后台推理全时长当独占桌面，也不能在未授短lease时抢焦点。当前root通知T01唯一lease，政策文件中当时T06 owner仅属历史。

Windows静态/Mac语法、oracle actual、默认3skip/显式65零skip、无真实API/双OS/五真人/签名渠道/CI/合并及首38失败完整raw缺失，均不因环境安装或当前桌面政策变化变成通过。模型无法验证关键项应明确无法验证，不预填Pass。
