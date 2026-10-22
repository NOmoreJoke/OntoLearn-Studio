# 本轮验证记录

工作树 `T01-c1-remediation-20261022`，起点 `c0b61fd245c1b3bd2a84e488f00a742a1942fd8c`；批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。实际命令的完整 argv、cwd、UTC 起止、exit 和双流以工作区外 `outputs/20261022_review_backlog/T01-C1-remediation-20261022/raw/<run>/receipt.json` 为准。后续新候选与测试脚本身份另行固定，以下不提前称最终树通过。

| run                                                             | 实际命令/检查                                     |  exit | 证据与边界                                                                                                                                             |
| --------------------------------------------------------------- | ------------------------------------------------- | ----: | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| environment-npm / environment-uv                                | npm ci / uv sync --frozen                         | 0 / 0 | 本树独立依赖；不是产品测试                                                                                                                             |
| surrogate-base / surrogate-current                              | 自写脚本分别导入固定 base / 本树 Store            | 0 / 0 | 默认 format2 私有定义分支，高低孤立 surrogate 均交易前拒绝、dump 不变、随后合法 Unicode 提交成功；不能扩为全部输入/wire证明                            |
| c1-invalid-name-boundary                                        | 既有 test_invalid_names_are_strict_and_zero_write |     0 | 7 passed；其中 C1 名称 U+D800 按 CreationFault input 拒绝                                                                                              |
| documentation-format-check                                      | 对本轮三新说明与迭代澄清实际 Prettier check       |     0 | 使用 --ignore-path /dev/null 精确文件，不因 docs/reviews 被默认忽略而称已检查                                                                          |
| proposed-config-patch-check / proposed-history-copy-patch-check | 两获准补丁在实际新树 git apply --check            | 0 / 0 | 随后才按窗口应用；不覆盖并发配置                                                                                                                       |
| applied-document-static-check-02                                | 锁定 Python 3.12 的 stdlib 静态核验               |     0 | root pyproject 仅三路径 format 例外；38 旧件不变；三副本 AST/非代码正文/链接等价；锁、package scripts、engine pyproject 不变                           |
| applied-ruff-format-check                                       | uv run --frozen ruff format --check .             |     0 | 实际项目根执行；只证该门，非完整 npm check                                                                                                             |
| build-01                                                        | npm run build                                     |     0 | 真实三段构建；未启动 Electron，不是 GUI/native或打包                                                                                                   |
| verify-sources-01                                               | npm run verify:sources                            |     0 | 实际核对 12 个归档源文件                                                                                                                               |
| full-check-01                                                   | npm run check                                     |     0 | 完整合成命令实际结束：Vitest 1125 passed，Python 2969 passed / 44 skipped。绑定 A 配置与两新 native 脚本首固定版，尚未包含后续旧 e2e userData 隔离补丁 |

| full-check-02 | npm run check（应用三旧 e2e v2 后） | 0 | 2026-10-22 16:13:06.318446Z 至 16:17:56.778175Z；Vitest 1125 passed，Python 2969 passed / 44 skipped；stdout 8675 B / SHA256 `81afa6eeda05b6813c760a2deaeac9be143ad6965cc806d2a315815a1e75d7ca`，stderr 0 B。覆盖本轮代码/配置固定版，不含 GUI 验收 |
| original-e2e-fixture-01 | .venv/bin/python scripts/prepare-i04-fixture.py 自有新 fixture 目录 | 0 | 正常合成真实 SQLite JobStore；无 GUI；后续原完整套件使用此 fixture，不能因缺 fixture 跳过 I04 reload |

首次静态文档核验误用了主机 python3，因缺 tomllib 在 import 阶段实际 exit 1；未改被核对象。失败说明保存在 `static-document-check-first-failure.md`，精确起止未另捕获，不补造。后用锁定环境的 check-02 通过，不能改写首失败。

本轮没有产品补丁：所核 52 项产品/测试字节仍等冻结 423；诊断/Unicode 的有限结论见独立 `independent-product-triage-review.md.raw`，共享契约处置见 `shared-contract-disposition.md.raw`。这些独审均未替模型关闭原问题。

两新脚本首固定版已通过独立静态审查，见 `independent-native-runner-review.md.raw`；A 实际落地的独立复核见 `independent-format-remediation-review.md.raw`。两者都没有执行 Electron/GUI 或代签 native 通过。

原完整 e2e 的普通 launch 缺独占 userData；总控精确三路径 v2 窗口已生效并实际一次应用（未叠加 v1）。五个框架 launch 加独占路径与实际 app.getPath 读回、JSON 附件和 exact guard；I04 共享 appArgs 覆盖其原生分支。112 项原 expect 与 3 项原 skip 保留，CSP 旧原生块不变。完整 check-02 已针对该版结束 0。原完整套件尚未启动；实际执行仍须真实正常 fixture、全部用例、Mac 两个 Linux-only skip 如实记录，不能拿新 native 脚本替代。

原 MiniMax Not Pass、两审原始失败、覆盖缺口与未知项继续保留。真实运行只在总控桌面交接后执行；direct-native 范围是本候选 Mac 桌面 health/crash/hang/真实选择与恢复兼容，不冒正式创建业务或全套 e2e。全套框架测试的 stub/hang-monitor 限制与 direct-native 的真实运行分别记账。

身份核验先误把含 7 份文档的 59 路径清单断言为 52，首失败见仓库外 `pre-freeze-identity-first-failure.md`；改正口径后确认 52 项产品/测试字节均等 423，仅获准迭代说明补充不同。随后 `pre-freeze-identities-02` 在 Electron 二进制存在断言失败（exit 1），因为本树只有锁定 npm 包，尚无 dist；`pre-freeze-identities-03` 记录缺失事实并完成身份核验（exit 0），不能称二进制已可运行。文档证据整理另有一次主机 Python stdin 编码错误，解析阶段未写文件，后续使用锁定 Python 与显式 UTF-8。各首失败保留，不倒填为通过。

实际应用的三旧 e2e v2 已独立静态复核，见 `independent-original-e2e-userdata-v2-review.md.raw`：逐 hunk 重建与实际三文件一致，112 旧 expect／3 skip 完整；没有执行 e2e。
