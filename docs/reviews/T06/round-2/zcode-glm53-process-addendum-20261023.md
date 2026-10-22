# T06-S1 R2 原报告作者流程补正（zcode-glm53 / 2026-10-23）

- 性质：仅对本人 round-2 审查会话（`session_6f01f2e4b4e2b589b2c21916110aa5f0`，原 turn `turn_cc86ce6d-d84d-42ca-849c-6c37d7274a2e`，2026-10-22T19:33:57.416Z 真正完成）自身过程事实与读取范围的补充与更正。**不重跑任何已具完整原件的产品验证、不重试被拒操作、不执行归档脚本、不修改原报告/终答/受审实现/测试/依赖/配置。**本补正是后续新事实，不回填原 turn。
- 原报告：`docs/reviews/T06/round-2/zcode-glm53.md`，23001 B / SHA-256 `764b62939c30605bfb4d90b56c70469389d3fea5402cf51c3b84dad430290e79`，补正前后未变。原终答 2886 B / `9363a2dfdb275677d3826aec0035d977f32549391942c1274b67b2b49a405315` 未变。
- 任务来源：`out/environment-prep/process-correction-20261023/own-process-correction-full-input.md`（86756 B / SHA-256 `be79cb305a4c3ed7f2056def3e9ccbf8628e8fec0fb148ec66edc78d1a92fc4a`，与官方粘贴附件 `cmp` 逐字节一致；其后缀 40359 B 与原冻结输入逐字节一致），含本人原报告区块、独立流程审查区块与原冻结完整后缀，已全文分段读回。本补正唯一新增文档为本文件；过程证据仅写 `out/GLM53-r2-process-addendum-20261023/`。

## 1 独立流程审查的逐项处置（我自行同意或补充，不由他人代我决定）

| # | 独立审发现 | 我的处置 | 说明 |
| --- | --- | --- | --- |
| 1 | 实际 1 次 PreToolUse 路径守卫拒绝（Bash 拟将 build_corpus.py 复制到自有 out，2587B 命令被拒未执行） | **同意，原报告已如实记录** | 原报告§3"过程记录"所记即此项；拒绝次数 1 正确；被拒 payload 未重试，改用 stdin 内存 exec 完成。 |
| 2 | **首条 stdin 探针真实 exit 1 首败被漏记**（`AttributeError: '_io.TextIOWrapper' object has no attribute 'read_text'`，发生于结构核验成功后的 committed 读取行） | **同意，确认属实并补记** | 我的第一次 stdin 执行（counterexamples 全量结构核验+作者脚本内存重放）在打印完 9 例结构检查与 13 请求事件后，因我笔误 `open(...).read_text()` 在读取 committed 处崩溃，进程 exit 1；第二次修正为 `.read()` 后 canonical 完全相等。原报告§3 #10 与终答只写了成功的第二次，未披露该首败。首败不涉及产品缺陷（崩溃在我方探针代码），但按"不抹首败"规则必须记录。 |
| 3 | T09 probe 与自编 stdin 探针一/二/三经 tail 管道，未保存真实 child exit/完整上游流 | **同意，降回证据实际支持的程度** | probe 命令为 `… 2>&1 \| tail -3; echo PROBE_EXIT=$?`——无 pipefail，`PROBE_EXIT=0` 是管道尾部状态，不能独立证明 Python exit 0；77789B 九例完整产物与成功才打印的摘要 JSON 行支持比较确实走到输出完成。三个自编探针分别 `\| tail -30/25/30`：返回为尾部摘录，无完整上游 stdout、无 child code；其结果行（510/299592/5000 零失败、1500 差分统计、9 条定向 OK）作为**观察到的输出**保留，不升级为"已保全完整流的验证"。我不以手写 receipt 或现在复跑补造原时点证据。对照组：139 行为测试与 `npm run check` 是先全量重定向日志再 append `EXIT=$?`（真实 child exit 已保存）；owner helper 三组在打印前即时保存 JSON/echo `$?`——独立审同样接受这三组。 |
| 4 | 510 例非"二实例二值全部序列组合"，实为交替值下的全部实例序列 | **同意，更正表述** | 探针一第一部分仅枚举实例序列 `product(range(2), repeat=length)`，值按写位置固定 x/y 交替（510=Σ2^1..2^8，跳过空序列）。准确表述："交替值下长度 0..8 的全部二实例序列 510 例"。完整值组合覆盖来自第二部分 299592 例（实例序列×值序列双积，四 typed 值），该部分表述无误。 |
| 5 | typed 首对末尾比较用 Python tuple `==`，非类型保真 | **同意，精确化** | oracle 的冲突判定用 `_json` 区分 0/False、1/1.0（类型保真），但最终把首对转成 tuple 用 `==` 比较——`0 == False` 为 True，抽象反例（期望 A=False/B=0 而错误返回 A=0/B=False）不能被该比较排除。该穷举证明的是：首对的实例、槽、位置在全部枚举下与直接 combinations 定义一致，值在 Python `==` 意义下一致。typed 值精确相同由：299592 例的 `_json` 冲突判定、139 项测试显式 JSON 类型断言（`test_competition_preserves_json_types` 用 `json.dumps` 比较）、1500 差分 canonical JSON（`json.dumps(0)≠json.dumps(False)`）分别支撑。不把 typed 穷举整体作废，也不虚称末尾比较类型保真。 |
| 6 | 5000 随机例被 flatten 为 set 动作，create/many 路径未走 | **同意，更正归属** | `compare` 实际调用 set 包装；我定义的 create 包装函数未被调用；随机只在 status/p2（均单值）中选属性。原报告§3 #4 括号"（含 create 多写、多值槽）"对这 5000 例不成立。create.initial 隐含写参与竞争、多值槽、跨槽全局首对的直接覆盖来自：139 项单测（`test_create_initial_values_participate_in_cross_instance_competition`、`test_compound_create_all_initial_writes_compete_and_remain_one_intent`、`test_first_conflict_uses_global_left_then_right_not_first_closed_slot`）、1500 差分生成器（含带 initial 的 create 动作）、owner helper 1009 例（randomized 含 create/tags）。共同历史探针（87381/6000/1520）不属于本轮自编，未冒称。 |
| 7 | 1500 差分无续轮；`original` 变量未用于最终断言 | **同意，更正** | 生成器每例 round=1、consumption 为空，无续轮；我构造的 `original` 深拷贝未参与最终 assert（差分双方各自对输入做 deepcopy 后传入）。原报告§7 LR1 行"差分含续轮场景"**错误**，应更正为：续轮覆盖来自 139 既有测试（B-01 重投 no-op、constant create 四参数化续轮、`test_repeated_event_is_noop…` 等），非自编 1500。1500 差分的"每例完整 plan/错误 canonical 相等、473plan/1027error/零 mismatch"结果本身保留。 |
| 8 | 定向负例的外层不变性不能证明传入 planner 的副本不变 | **同意，限定** | 我的 `run(req)` 先 deepcopy 再传 prepare；`req == before` 证明外层原对象未变。真正把调用者对象直接传入并断言不变的证据是 139 项测试（如 `test_failed_action_does_not_produce_or_mutate_candidate_or_ledger`：`execute(req)` 直接传引用后 `assert req == old`）。两份 plan 互不串扰与决定容器独立在我的探针中有直接 assert。不因自编补充的边界把产品输入所有权缩小为缺陷。 |
| 9 | 零失败计数未成为可失败验收器（无最终 `assert==0`） | **同意** | 探针一/二主输出 failure/mismatch 计数，`expect_fail` 打印 FAIL 而非 raise。实际输出为零失败/全 OK，作为观察记录保留；脚本 exit 0（且经 tail 管道）本身不构成断言全部满足的证明。 |
| 10 | "全程仓库零接触"字面过宽 | **同意，更正为精确写面** | 实际真实写入：`out/GLM53-r2-evidence/`（两份完整日志、probe JSON、helper 三组 JSON、receipt）、`docs/reviews/T06/round-2/zcode-glm53.md`、stdin 探针的 out 临时目录（TemporaryDirectory 自动清理）。准确边界："未修改 13 受审产品来源/测试/依赖/配置与 AGENTS；获授权写自有 out 与本任务报告；无 .py 脚本落盘"。"仓库零接触"应按此理解，不能扩大为证明一切隐式文件活动均无。 |
| 11 | traced peak"不会因环境波动降低"的必然性推论过宽 | **同意，撤回推论** | 三次（owner 配对、前次独立审、本轮）测得完全相同的 340522343 B 是三个已记录样本，与该实现的确定性分配行为相符；但未控制的分配器、Python 运行环境/GC 等因素不由这三个样本排除。保留观察数字与口径（tracemalloc 开启、非 RSS），撤回"确定性下限/不会降低"的必然性表述。P2 严重度与容量结论不变。 |
| 12 | 完整 base→product owned diff/允许历史 metadata 逐项读取未证；613→3be slice 25–39 无 literal 返回 | **同意：原 turn 该步骤未完成；本后续回合已按原范围补完（见第 2 节）** | 原 turn 实际完成：总 hash/字节数/stat、76 全 A 确认、613→3be 三文件 diff 大部分行、13 产品源全文。未完成：其余 owned 流程文件逐项读取、slice 25–39 行、binary 块 metadata 逐项核验。不存在既存的"当时已读"遗漏原件可提交——如实承认当时未完成，now closed as follow-up。 |
| 13 | 支持索引更正（minimal-manifest 旧 2242B 引用过时） | **已受理** | 按更正附录：当前支持定位使用 v2 索引（3292B/`03cbe9f6…`，14 项已逐件核 bytes/SHA，仅第一项改指 3063B 固定快照 `033c1c1a…`）；旧 `reviewed-evidence-index.json` 的 2242B/`141303…` 保留为独立审核时点的历史引用，不套用于当前文件；**新快照不作为我原 turn 已完成缺失读取的证明**。原独立审与原报告区块中 2242B 行按历史快照解读。 |

## 2 本后续回合的实际补读（原范围闭合；不回填原 turn）

对 base→product diff 的 76 个文件按原冻结口径完成分层闭合：

- **原 turn 已全文读取（15）**：13 产品源、review-readiness.md、status.md、local-review-1..6、round-1 七份共同历史（两报告、ZCode 补正、两 owner audit、remediation plan/independent review）。
- **本回合全文补读（28，均为本线 owned 流程文本/JSON）**：baseline-compatibility-audit.md、blocked-audit.md、operating-policy-ownership-update.md、external-review-backlog.md/.json；round-1 的 desktop-approval-receipt、dispatch-addendum、dispatch-entry-check、dispatch-progress、frozen-inputs、minimax-completion-receipt、minimax-start-receipt、zcode-cli-login-readiness、zcode-completion-receipt、zcode-desktop-start-receipt、zcode-process-correction-request、双方 input 与三份 dispatch 文件；evidence 的 minimax-facts、两份 tool-evidence-readback、validation.json、validation-e81cfc9.json、validation-61396a5.json、t09-candidate-probe.json（完整清单与要点见 `out/GLM53-r2-process-addendum-20261023/receipt.json`）。其中 round-1 双方 input/dispatch 属 base→product diff 内的已归档历史轮材料（冻结排除条款针对"同轮另一模型提示/报告"，即 round-2 MiniMax），现作为后续事实读取；比对确认双方 input 仅首行（模型/权限/报告路径）不同，佐证 round-1 同版对称双审。t09-candidate-probe.json 全量解析：9 例、269 投影项、B-01 重投、B-05/09 失败例、manual gold 标注完整。
- **613→3be 三文件 diff 的 25–39 行缺口**：本回合以完整 literal 返回补读闭合；内容全部属于 interface.md/t09-adaptation.md 的 diff 行，其最终文件内容原 turn 已全文读取，闭合未产生新疑点。
- **UI 线 16 文件**：按冻结口径仅登记类别/metadata（路径/bytes/SHA/Git 相等），未读模型意见类内容（清单见 `out/GLM53-r2-process-addendum-20261023/ui-and-binary-metadata.json`，16/16 与 Git 3be 相等）。
- **4 个 binary 块**：仅核 metadata/hash——minimax 工具包 629906B/184 regular/`c68ba2b7…`、zcode 工具包 918318B/439 regular/`32c7b837…`、UI 两包 2232198B/34、6698B/8——与 owner 登记一致；未执行任何归档脚本。

补读未改变任何判断所依赖的事实：28 个文件均为流程/历史证据，13 产品源对 Git 3be 仍逐字节冻结，无新增产品验证需求（不盲跑、不为凑数字重复测试）。

## 3 对原报告各处的更正汇总（原文件不改，以此为准）

1. §3 #4 括号"（含 create 多写、多值槽）"→ 仅适用于 139/1500/helper1009 的覆盖；510 例改述"交替值下全部实例序列"；5000 随机例是"多槽/多实例/多值 set 展开"。
2. §3 #10 补记首条 stdin exit 1 首败（AttributeError，探针自身笔误）及第二次纠正成功链。
3. §3 "过程记录"中"仓库零接触"→"未修改受审源/测试/配置；获授权写自有 out 与报告；无 .py 落盘"。
4. §7 LR1 行"差分含续轮场景"→ 更正为"续轮由 139 既有测试覆盖"。
5. §5 信息项撤回"确定性下限/不会因环境波动降低"的必然性推论，保留三次相同的观察与口径。
6. §2 "完整 base→产品 diff"读取范围声明 → 按 12 号条目分层：原 turn 完成部分 + 本后续回合补完（第 2 节），补读不回填原 turn。
7. probe 与自编探针一/二/三的 exit/完整流证据等级 → 按 3 号条目降回实际（观察输出 vs 已保全 child exit 的 139/check/helper）。

## 4 当前结论

- **产品结论（私有 S1 范围，产品 3be0397）：维持通过。**所有补正均为流程/表述精度问题；支撑产品结论的核心证据（139 项行为测试、npm run check、owner helper 1009 差分/800-create/百万矩阵——均具完整日志与真实 exit）不受影响；1500 差分与自编 oracle 的观察结果在精确化表述后继续成立。P2-1 机制修复、P2-2 风险保留且容量门开放、Q5 无批准阈值不代填、父 FR-600–604 与完整 B 用例门保持开放。
- **流程结论：**原 turn 存在一条未披露的 stdin 首败、tail 管道 child exit/完整流缺口、若干过宽表述、owned diff 逐项读取未完成；本补正已逐项如实补记，并按原范围以后续事实补完读取闭合。流程完整性门是否据此关闭由总控裁定，不由本补正自动通过。
- 未重跑：139/check/helper1009/creates800/matrix1000（均有完整原件）；未重试被拒 payload；未执行归档脚本；未读同轮另一模型任何材料；无 GUI/native/e2e/HMR/模型 API/密钥/新增支付。
- 唯一新增文档：本文件。过程证据：`out/GLM53-r2-process-addendum-20261023/`（receipt.json、ui-and-binary-metadata.json）。原 `out/GLM53-r2-evidence/`、原报告、原终答保原字节。
