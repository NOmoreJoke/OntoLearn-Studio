# T11 owned fixes 独立实现审查

2026-10-23。审者：独立 agent `/root/t11_independent_review`。本报告是本线独立内审，不是 GLM-5.3 / M3.1-Flash 指定工程复审或发布批准。

## 固定输入与执行边界

- 审查树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T11-fix-audit`。
- 分支：`feature/weekly-t11-fix-audit`；完整 HEAD：`640cf49d627dc4796bc90ee37abf9bb3857eb42b`。
- 全差异：`692077da9754a303915798789b7b0c5b4f609125..640cf49d627dc4796bc90ee37abf9bb3857eb42b`，14 个路径，全部阅读。
- 起始工作树仅 ` M AGENTS.md`；已全文阅读最新指南，不暂存该文件。
- 阅读批准 triage 四件及总控精确 `iteration-control/2026-10-21-weekly-release/.private/T11-triage-owned-plan-controller-audit-20261023.md`；对照 PRD FR-105、FR-1000、11.2、12.1 第八步、E.2、G.6。
- 仅进行源码、文档、Git 差异及固定来源 hash 静态检查。`git diff --check <base>..HEAD` 无输出、退出 0。未运行专项或全仓测试、构建、安装、数据库、collector、GUI、原生/API/网络/签名验证；不把 owner 观察的 105 专项或全仓结果写成本审者运行。
- 唯一新增/提交文件为本报告；不修改产品、测试、配置、旧报告或总控状态。

## 结论及待修问题

本固定候选的实现差异中，未发现新的可具体成立的错误接受或过度拒绝反例。下述 W6 当前入口缺口须在最终冻结前处理；本结论不关闭原 18 项或 M NotPass，也不认证未运行的目标平台与真实产品行为。

### R1：当前状态入口仍指向旧候选，且未精确披露首轮 raw 缺口（P2，文档）

位置：`docs/reviews/T11/status.md:16`、`:18`、`:30`、`:36`、`:56`；入口引用见 `docs/iterations/T11/acceptance.md:3` 和 `docs/release/README.md:3`。

复现：在本 HEAD 按两份当前说明进入 status，仍见 65 专项/695 TS、三个探针、v2 和旧核验器 hash 被称为当前；第 36 行把 `7d28fdb` 称为当前恢复入口，第 56 行仍称“当前仅计划，无产品代码/测试/collector修改”。这与已提交 v3、IO、collector 及新测试不一致。第 18 行总括“失败原件与重跑日志保留”，没有在当前入口分列首 38 项首失败缺独立完整 raw、只有摘录/transcript 的已知边界。

影响：下一审者按唯一状态入口可采用旧候选或旧验证范围，并误读失败原件完整性；对应批准 W6 及仍 open 的 M-F-K / M-F-L。不是运行放行反例，不修改其原严重度。

最小修正：在新当前入口注明绝对日期、适用产品 SHA、v3 和新增测试/collector范围、真实新验证原件及旧 7d28 记录的取代关系；明确首 38 缺完整 raw 与后续现存归档分列。旧 JSON、原报告、历史 hash 不追改。新验证仍须按实际退出和 skip 记载。

处置状态：owner 已确认正在主树准备该流程收尾；本审查树未包含修正，故本报告保留 R1，待精确新字节复核。

## W1–W6 静态核对

| 工作包            | 本候选依据与判断                                                                                                                                                                                                                                                                      | 仍保留的边界                                                                                                                   |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| W1 比较与真人口径 | `verify.ts:218–245,911–1011,1056–1078`：v3/case、外部源 hash、两迁移 case literal g6-conflict；六层非空仅限 G.6，facts/ownership 模板边界保留；全部 22 MIGRATION_CHECKS 未删。`verify.ts:885–905` 与 user-study 第 25–29 行：八步 core 与 transferCompleted、独立迁移和实际辅助分记。 | 领域 payload 完整性和真实尝试先后仍须正式 adapter/原件；不自动裁决 F01/F16，不将新目录或换输入恢复独立资格。                   |
| W2 服务与基线     | `verify.ts:14–45,562–579,843–860`：批准 Q9 tuple/source SHA 与独立 freeze 同时匹配；evidence 固定唯一 manifest SHA、PRD SHA、版本和精确 17 路径。实际读取 decisions 第 21–29 行，原件 hash 为 `def9817d…d84a7`；固定 873 Git manifest hash 为 `aaaef2c0…ac39e`，与常量一致。          | 静态来源约束不证明服务可用或 API 评估；内容 hash 仍来自 T09 唯一 manifest，没有复制第二权威基线。                              |
| W3 IO 与分支      | `verify.ts:345–450`：打开后 fstat、限额后分配、readExact 有界循环、同 fd hash/结构、结束额外字节和元数据检查、finally close；CLI 第 12–16 行先 readJsonFile 再 parse/schema。`:1067–1077` 显式缺目的资产 fail/continue；第二次 schema parse 已删，finite(now) 保留。                  | O_NOFOLLOW/O_NONBLOCK 依平台能力；祖先目录稳定条件明确，未声称消除全部竞争。工程 16MiB/8GiB 不当 Q5。                          |
| W4 collector      | Mac 全部外部系统命令使用绝对路径，pending/step、EXIT/信号失败标记及最终 complete；Windows 状态/步骤和首次 raw 分开保留，PE helper 在读取前核 64 字节 DOS 和 offset 范围，异常固定为 PE_INVALID。                                                                                      | 本审者未运行 bash-n、PowerShell 或目标 collector；Windows、Mac 成功/失败/防覆盖仍须获批目标运行。marker 不等于签名或原生通过。 |
| W5 来源与回退     | `verify.ts:777–804`：严格 collectorStatus 和 check 绑定，同包声明引用字节均读/核 hash，包 hash 必须等于候选；恢复及每上一版资产报告新增两项具名回退 check。                                                                                                                           | 工具不解析 T03 清单成员或认证安装/解包原件；真实同包关系仍待独立原件对照，不能仅此关闭 M-F-H②。不实现第二恢复器。              |
| W6 信任/流程      | README 明确结构与签名链、墙钟、祖先竞争/同包来源边界；user-study 明确原件核验责任；acceptance 区分默认四 skip/显式固定探针、oracle actual、fresh 双指定门。                                                                                                                           | 当前 status 未同步，见 R1；旧报告/JSON 原样保留。所有原 57 P0、1000轮/每轮1000动作、双目标、模型、真人、CI/合并/渠道门仍有效。 |

## 测试审阅及后续验证

已全文静态阅读两份专项测试及 comparison fixture。新增正例确实经过 generic 合法空层；负例分别处理模板、G.6 六层、case/版本、Q9 pin、collector 缺失/异常、同包包 hash、回退缺项、八步 4/5 与 3/5、实际辅助和生产 profile。固定探针只按固定 873 Git 输入物化临时 fixture；actual 由 oracle 构造，文档如实说明不表示 50 项产品运行。新增第四探针默认 skip 是公开条件，不能作为联验通过。

IO 小文件模拟覆盖解析前限额、非 regular、增长、短读、读异常关闭、叶替换、PE/koly 和大文件增长；源码保持同 fd。当前测试仍可补三项定向断言：重复目标时明确出现 MIGRATION_DESTINATION；CLI freeze 伪 now 被当前墙钟覆盖；CLI 超限返回 2 且不输出输入正文。owner 已告知准备补充；这属于后继测试变化，未包含于本固定 HEAD，不在本报告中冒称通过。目标 collector 真运行按原票另验，无压力实验、SQLite 损坏 HOLD、新 native caller 或服务授权扩张。

## 原 18 项处置边界

下表仅记本轮静态观察，不作正式关闭；全部维持 **open**，原 M NotPass 保留。

| 原项  | 原级别 | 本轮观察                                                 | 状态 |
| ----- | ------ | -------------------------------------------------------- | ---- |
| M-F-A | 高     | v3/外部 case pin/G.6 双向固定已实现；模板拒恢复。        | open |
| M-F-B | 中     | Q9 source/批准 tuple/freeze pin 已实现。                 | open |
| M-F-C | 中     | evidence 固定 profile/17 路径已实现。                    | open |
| M-F-D | 低     | 八步及 transfer 条件保留，独立成功分记；不采仅七步放宽。 | open |
| M-F-E | 低     | acceptance 四 skip 与历史结果已澄清；status 待 R1。      | open |
| M-F-F | 低     | 恢复/逐旧资产具名两项新增 check。                        | open |
| M-F-G | 低     | 主持人与独立验收原件责任明确；工具只 hash record。       | open |
| M-F-H | 低     | 状态/PE/同包 check 已实现；真实 T03 来源对照待验。       | open |
| M-F-I | 低     | 结构/声明不等于签名与实质格式的边界明确。                | open |
| M-F-J | 低     | 当前墙钟及来源/偏差责任明确；工具不认证时钟。            | open |
| M-F-K | 低     | 旧记录保留；新唯一当前入口待 R1。                        | open |
| M-F-L | 中     | 首 38 raw 缺口须在当前入口分列，待 R1。                  | open |
| Z-F1  | P4     | 重复 schema parse 删除，finite 保留。                    | open |
| Z-F2  | P4     | CLI/普通/大文件/结构同 fd 与限额实现，祖先条件明示。     | open |
| Z-F3  | P4     | 缺目的资产显式 fail/continue，建议补直接断言。           | open |
| Z-F4  | P4     | Mac 系统命令绝对路径覆盖最前门与 xcrun。                 | open |
| Z-F5  | P4     | PE 长度/offset 界限与固定错误；真实 Windows 未验。       | open |
| Z-F6  | P4     | 保半成品/失败原件并拒无 complete；目标运行未验。         | open |

owner 修 R1 或追加测试后须以精确新差异补复核；无变化部分不机械重审。随后新同候选两份完整指定审查、真实终态/全文收件/全部意见处理及原 CI、正常合并和远端核验要求均不变。

## 固定 delta 复核：33894063

同日收到 owner 固定补充 `33894063fcf17bc865f4c91556a8ca01845812e7`，只读完整 `640cf49d..33894063` 差异，恰为 `tests/unit/t11-release.test.ts` 与 `docs/reviews/T11/status.md` 两路径；未切分支或引入其余改动。生产源码保持原固定候选字节。

**R1 文档残留已关闭。** status 新第 1–14 行置顶精确日期、工作树/分支/base、首个实现 SHA、当前修复范围，明确下方“当前/active/仅计划”等均为历史；旧 7d28/v2/65/695 不作新验收。新第 12 行分列首 38 缺独立完整 raw 与后续 48 现存归档，不追写旧 JSON。新第 8 行把 105/735/1052 明确限定首次修复验证，新增回归另验，未把旧计数冒用为后继最终 SHA 通过。M NotPass、18 open、双指定/CI/合并/真实来源及 F01/F16/Q5 边界继续保留。本次只确认该文档修正；没有重读/认证 owner 所述 tar 48 成员、测试日志或正在形成的 verification/handoff 等后续流程原件。

新增四个运行用例的代码静态审阅无残余问题：重复目标同时断言 TARGET_MATRIX 与 MIGRATION_DESTINATION；伪 now 用未来一天的真人时间验证 CLI 覆盖后产生 USER_STALE，而非只靠 synthetic 的退出 1；manifest/freeze 两超限路径分别断言 exit 2、空 stdout 和最后非空 stderr 固定错误码。该 stderr 断言保留 Node 警告而不屏蔽或改共享配置。此前两条断言首败及后继重跑由 owner 另存，未在本报告中宣称本审者运行或新增 109/全仓通过。

截至此精确 delta，静态内审无待修的新实现或文档问题；全部 18 项仍 open、原 M NotPass 不变。真实运行证据、新完整候选冻结与两份全新指定工程审查仍按原门继续，不能由本内审代替。
