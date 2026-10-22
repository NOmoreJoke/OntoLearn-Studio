# T09 replacement-r1 首收件限定结构审查

**通过：四份指定 JSON 的内部身份、首输入记录、阶段口径与未完成边界一致，未发现实质矛盾。** 这是结构收件结论，不是 native 原件验证、模型/产品 Pass 或终态收件。

2026-10-23（Asia/Shanghai），独立 Codex 子 agent `t09_prd_audit`。只读本目录 `launch-acceptance.json`、`native-first-input-receipt.json`、`zcode-operator-own-receipt.json`、`minimax-operator-own-receipt.json`；唯一新增本报告。未跟随其中路径，未读取原生模型/global/数据库/peer/源码/测试，未 GUI、执行文内命令或重取旧 32 源/输入证明。

## 身份与阶段

| 方  | 新 SID                                     | 原 turn                                     |
| --- | ------------------------------------------ | ------------------------------------------- |
| Z   | `session_1d54a3bdcdcb436f5693f8a1f6c41544` | `turn_9bfca954-5f33-42c8-ac6a-c38344f8c7e0` |
| M   | `mvs_4a0e67fa3d5949eb910022a5c96822fb`     | `12d877f3-1c57-46bb-ad32-a609bc2a0ba3`      |

各方 SID/原 turn 在三处对应记录一致，ownCWD、common review HEAD `72aa83a80a973a3edeb62ed95518bf1a22178985` 与本人 fresh 收据一致；base5f/product765/processd969 和 prepared-input commit 分列。仅 S1 两新任务受理，N0 未派发，不混入其他候选。

两份本人收据明确是 fresh UI observation，不是 template；UI model/effort/permission、own path 观察及更新时间单列。`acceptedAtUTC` 仍 UNKNOWN，不从更新时刻推算 backend 受理时间；后继填入的 originalTurn 明列 operator 授权窄路线来源及 native binding 时间，不伪作最初 UI 字段。此处只核文档结构，不独立证实 UI 或 backend 事实。

## 首输入与完成状态

Z 记录 75876 bytes / SHA `e7bc2a159c554df686f7d991d3912798d1e1caa7f08ba93f2cdacbd675c088ea`，与本人收据相同。native/UI 409 行包含末尾空行，冻结 logical splitlines 为 408；“去实际 tab 行前缀、409 行 LF 连接、不另补 LF”的表述与终止空行口径自洽，没有把 409 强改为 408。

M 记录 75943 bytes / SHA `18fbcbe32a1dd353e36c63a311db31f7257e2b0ef2ad538dc2084880ec47fe1b`，与本人收据及 launcher 声明相同。四次 Read 范围为 1–118、119–215、216–373、374–408，精确连续覆盖 408 行；offset 与后一段起点一致，gaps/conflicts 为空，terminal LF 明列。两方均声明没有用 expected 填补缺口。本次没有读取返回行原文或重建 native 字节，只确认这些记录的内部一致性。

Z lifecycle 只有 started，无正式 completed；M original-turn terminal_outcome 为 null，session 为 started。两方正式 terminal 均保持 UNKNOWN，report 均为 not collected，不把受理、输入完整性或任务开始当完成/Pass。报告写面沿已绑定冻结完整输入，不在本次另读旧 mapping 或实际报告，亦未声称已验证新报告写盘位置。

GUI release 在接受总表和两本人收据中均为 `2026-10-22T21:07:08.485Z`；后续 native binding/结构收件按单列时间描述，不被写成 release 后再次 GUI。正式来源事实仍属操作员收据，本审查没有独立操作或读取 native。

## 保留边界

旧 Z Pass 不继承；same/replacement pair Pass=false。旧 M 过程 Fail/aborted 和三 P3 有条件延期均明确保留，未借新受理将其关闭。operator-only 收件与模型独立审查分离；M 当前 own-turn 未观察到禁止发现调用的空列表明确限于已记录输入，不外推未来或未记录行为。

收据明确未启动产品测试/浏览器 setup/native/e2e/HMR/API/OS 工作，未改原输入、Goal 或发布状态。以上是文档声明的结构边界，本审查未进行新产品、环境、HEAD/32 源或 GUI 验证。后续正式 terminal、全文报告、全部意见与指定双审/父验收仍须另行收件核定。
