# F04 修复验证收件独立审查

结论：补入明确的 Chrome 后采样收据后，当前限定收件审查通过，未发现未关闭的收件矛盾。本结论仅确认材料、固定源码身份与验证记录自洽，不是重新实跑、指定模型双审、Pair Pass、正式领域或父验收通过。

## 实际核对范围

实读本目录 `phase-and-validation.md`、`validation.json`、`runtime-receipts.json`、`source-32-vector.json`、`source-start.json`、`fixed-chrome-preflight.json`、`f05-historical-stage-binding.json`、两份已有独审，以及本次明确补授权的 `fixed-chrome-postflight.json`。逐一解压核对 18 个 `runtime-streams/*.txt.gz`，核对本树两产品文件字节及 Git 提交元数据；对其余 30 路径只核 Git blob 身份，不读其源码正文。未跟随旧根或历史引用读取原件，未读取 global/native/`.mimosa`、Chrome 实体或配置，未运行产品、安装、构建、服务或 GUI。

| 关键收件                              | 字节数 | SHA-256                                                            |
| ------------------------------------- | -----: | ------------------------------------------------------------------ |
| `validation.json`（补后采样后的版本） |   4726 | `080f601fc28f6171ba3e358074d2540dc5a345c298befefc97bbe12a367476e3` |
| `runtime-receipts.json`               |  44945 | `fc8fe314e38e4d0d837bc4e6aaab09dcb2fa8285a05589837caa6374774d8d24` |
| `source-32-vector.json`               |  13896 | `a2362221a1cf3718636b491e8da6f7342a7943152c72792d48b3c5dc74047cd0` |
| `fixed-chrome-postflight.json`        |    998 | `df951e6584ff1b275e5003d4b02461860076d0f59b209f992f1a316bb192ad98` |

## 收据与源码绑定

9 份命令回执均含 argv、cwd、显式环境、执行 HEAD、起止时间、真实 child PID/returncode、两路径 before/after 与 stdout/stderr 引用。将聚合内每份 `receipt` 按其原 JSON 格式在内存重建，9 份均精确匹配所列原 receipt 字节数与 SHA-256；未读取输出目录中的独立原 receipt 文件。18 份 gzip 的压缩字节/hash，以及解压后原 stdout/stderr 字节/hash，全部匹配聚合声明，且每条 stream 与对应 receipt 的 channel 元数据相同。不是只核尾部摘要或 `losslessRoundTripVerified` 布尔值。

Git 实际核对：当前 HEAD 为 `d643c5a41f42d4d5395ab7d6c457c6e002cf481f`，tree 为 `fbbe968e500d98eed8277588a0a535036260f12d`，parent 为 `0cde6a11604214f4ff34d2a9fbcfb80b6f72bfd2`；该提交实际只修改以下两路径。两文件当前字节与提交 blob 完全相同：

| 产品路径                                                       | 字节数 | SHA-256                                                            |
| -------------------------------------------------------------- | -----: | ------------------------------------------------------------------ |
| `apps/desktop/src/renderer/src/learning/LearningWorkspace.tsx` |  18669 | `5bd90f57bdb25874839c7f43bd4c61e42cf46b945675129a8a59eadce149fa9a` |
| `tests/unit/learning-workspace.test.ts`                        |  27178 | `b779a723fe46545e10f7d98c39e9da8bf69238bc0d77f2416a9c3d8055ef005a` |

32 路径向量无重复，候选 32 个 blob ID 均与源提交匹配；其中 30 个与 `76596656908ed84e577e8202a602e3256d5febcc` 的 blob ID 相同，两个变化标记及字节/hash 与上述两文件相符。`source-start.json` 的修前两文件值与既有独审中的固定来源相符。

运行回执的 HEAD 确为 `0cde6a…`，不是后来才创建的 `d643c5…`。材料正确声明运行于未提交候选，凭两路径运行前后快照绑定后来源提交；首轮测试文件仍为 `27162 B/b45db359…`，locator 修正及最终完整检查为 `27178 B/b779a723…`。本收件核验不把两路径快照扩写为运行期间全树持续不可变证明。

## 各轮结果保持分列

| 运行阶段                              | 回执退出码 | 原 stdout/stderr 支持的结果                                                                                                                      |
| ------------------------------------- | ---------: | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 首轮学习组件与纯测试                  |          1 | 39 passed / 1 failed；22 个组件案例中 same-context-zero hint 的宽泛 locator 在点击处发生 strict mode violation，未到产品回执 guard；失败未被覆盖 |
| locator 受影响案例筛选复跑            |          0 | 1 passed / 21 skipped；明确属于 `-t` 筛选，不当作 22 项全通过                                                                                    |
| 原完整 `npm run check`，显式 headless |          0 | 17 个 Vitest 文件、670 passed，无 skip；1094 pytest passed；lint、format、types、build、ruff 的完整链条走完，stderr 为空                         |
| `npm run verify:sources`              |          0 | 原 stdout 明确核对 12 个归档源文件，不沿用早先回报的 10                                                                                          |
| 两路径 `git diff --check`             |          0 | stdout/stderr 均为空                                                                                                                             |

完整运行总数与 22 个组件案例（含 6 个新增）及 18 个学习纯案例的材料口径一致；最终 stdout 只给总计，未逐条打印 22 个组件名称。本审查未通过重新运行取得这些结果，以上是对保存回执和原输出的独立收件核对。普通 `format:check` 只证明其默认匹配范围，不扩写为新审查文档的显式格式覆盖。

## Chrome 后采样缺口与关闭

首个失败 suite 的原 stdout 确有 `T09 headless browser version: 155.0.8059.85`。筛选复跑及最终成功套件的捕获输出没有版本行，`validation.json` 明确保留这一差异，没有从 plist 或首轮输出补造后续 launch 的版本打印。

最初材料只含 preflight 和“前后一致”布尔断言，缺独立落盘后采样值；本审查先报告这一收件缺口。随后开发线新增 `fixed-chrome-postflight.json`，明确是新采样 `2026-10-22T21:55:40.702829+00:00`，晚于完整检查结束 `21:53:22.598595+00:00`，未伪装成原先未落盘比较的精确时间。其 executable `367696 B/6e156f2271cef44afce9db36a5b920e94518857b94a4160f082696f8c3bd1c9d`、plist `18856 B/0c994f7cd1de97963191ac6e54341f5d20a551a544606636b58fc1852ee2ee23` 与 preflight 一致，更新的 validation 正确引用它，限定收件缺口关闭。

这是前后两个静态记录的内部核对，不是本审查者重读 Chrome、不证明连续文件监控、实际浏览器进程映像或 OS sandbox 隔离；材料也没有作这些声明。

## F05 与保留门禁

F05 新旁注与 sidecar 一致指向历史 `51cdc0e9d138c98cdd4ace865074a71883657a68` 服务/固定基线阶段，列出六个历史源路径及旧摘要 `3972 B/0acc4fafe1e334118afdb440295ca14d755babaff0494035aeeb087a9f789fa1`，将原 35/630/1087 与后来 UI、jobstore 及本次 670/1094 分列。本次仅核新材料对历史的引用自洽，没有重读旧摘要、六个历史源或历史原始运行证据，因此不另行宣称重新证明这些历史事实。

原两份独审保持其当时“静态、未取得运行原件”的事实边界，不追写为当时已运行通过。本次新收件报告补充后来的保存证据，不改历史结论。旧 Z 过程 FAIL、旧 Pair Pass=false、环境归因及 global 成功 UNKNOWN、先前操作者异常、13 旧项、3 个有条件延期、3 个父项及原 P3 严重度均保留。F04 实现修复与 F05 旁注不自行关闭根处置；正式领域/bridge/App/持久化/报告、指定新双审、Pair/父门、native/生产/发布仍未由本次收件核验通过。
