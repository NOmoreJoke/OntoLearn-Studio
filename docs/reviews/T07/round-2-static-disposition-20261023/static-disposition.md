# T07 R2 digest 意见静态处置及报告校正旁注

**当前证据不支持“完整运行值相等，只因摘要不同而误拒”的合并表述；也没有找到明文把重复/重排后的 Definition 规定为同一续跑输入。** 原 M 新 P2/P3 保留原等级、原报告与 root 待决状态；这不是降级、关闭或接受作者延期。尚未确认违反固定合同的源 bug，因此本次源修复 proposal 为空，不提交或实施三源路径改动单。

本次只读已封存 006/007/008 原 stdout/stderr/exit、三个原调用及与之直接相关的固定源码/PRD/本线提案。没有新审查任务、外审续发、GUI、原生 fallback、验证或 probe 重跑，没有自动排序/去重 digest，没有修改产品、测试、合同原件、作者报告、旧处置或 Goal。

## 1. 原证据对照：三次运行不能拼成全值等价

来源为已固定 72 成员证据包（SHA `6d95d96c8bea923b5f31477b6774d686932389a1c37960602cea2e7eb88cf070`）的 `final-minimax/runtime-originals/006-*`、`007-*`、`008-*`。本次仅核原字节与既有索引，不执行其代码。九个原文件的字节/SHA及准确 stdout 见 probe-output-comparison.json。

| 原运行 | Definition 差异 | 完整 Round / Checkpoint | 实际证明的子集 | 摘要 / 跨定义续跑 |
| --- | --- | --- | --- | --- |
| 006，`call_01a16586b29a7178bc975239` | 原 events 末尾再加首事件，同 ID 同内容；版本标签相同 | 原输出 `rounds_equal=False`、`checkpoint_equal=False`；两 status 为 succeeded | 本次没有定义/比较 semantic 投影 | digest 不等；没有续跑尝试 |
| 007，`call_01a16587a87774779300e2e7` | 同上，另一次独立运行 | 未比较完整 Round 或 Checkpoint；status 未打印 | 选定逐轮投影相等；最终 checkpoint.state、checkpoint.consumed 分别相等 | digest 不等；plain→dup 与 dup→plain 都拒绝 |
| 008，`call_01a165882f667474a0d117b1` | 逆序 events 元组，各 Event 自身的 sequence/内容未改 | 未比较完整 Round/Checkpoint，未单独比较最终 state；status 未打印 | 同 007 的选定逐轮投影相等 | digest 不等；只尝试 normal→reordered，拒绝；没有反向尝试 |

007/008 的所谓 semantic 投影实际只有六项：checkpoint.round、created、resource_completed、backlog、tuple(metrics.__dict__.values())、checkpoint.consumed。它不含 checkpoint.definition_digest/events/completed、每轮 checkpoint.state、input_events、before/end inference、trace、frozen_plan，也不比较 Result.definition/pending/status。007 额外打印的最终 state/consumed 不能移用为 008 的直接观测。

因此：006 是完整对象比较不等；007/008 是特定合成端口、特定 fixture 上部分字段相等。不能把 007 的子集相等回填成 006 的 rounds_equal=True，也不能把 007 双向拒绝回填成 008 双向拒绝。三组原输出均未打印 pending，不宣称 pending 相等。原报告有关全等、006/007 归属和双向范围的文字仅在本旁注校正，原稿保留。

## 2. 为什么身份差进入完整 Round，事件顺序又在哪里保留

固定产品 P=`f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`；读取来自本方固定 R 树。

- `scenario/model.py:178–197,226–228`：Definition 包含版本标签，也包含实际 capacity、events、initial、rules/behaviors/parameters、source/assumptions、max_rounds、initial_consumed 等。digest 对 `canonical(asdict(self))` 求 SHA；这是完整值的规范序列化身份，并不是只对版本标签求 hash，也不是任意原文件的字节 hash。
- `runner.py:64–83`：Checkpoint 的首字段就是 definition_digest；Round 包含整个 Checkpoint。`runner.py:147–154,296–303` 分别把当前 Definition.digest 写入初始及逐轮 checkpoint；Round 又保存该 checkpoint。故 digest 不等已足以导致完整 Checkpoint、进而完整 Round 不相等，哪怕某些状态/指标相等。006 没有输出逐字段 diff，本旁注不假称所有未打印字段都相同。
- `model.py:231–237`：event_catalog 拒绝同 ID 异内容，以 setdefault 保留首个同内容事件；字典保留首次插入次序。相同重复项不新增目录项，但原 Definition.events 元组的重复项仍参与 digest。
- `runner.py:152,275,300`：checkpoint.events 保存目录 values 的现有顺序；重复时是首次出现顺序，重排时可变。它没有按活动事件处理顺序重新排序后保存。
- `runner.py:230–239`：本轮实际待执行事件另按 `(sequence,id)` 排序。008 只逆序元组、不改 Event.sequence，因此该样本的执行投影可相同，不能据此认定原输入元组或全部依据相同。
- `runner.py:212–216`：pending 只是按 checkpoint.events 现有顺序过滤未消费项，不另排序。**静态条件推论，未新跑反例**：若两个尚未消费的未来事件在 checkpoint.events 中的次序互换，pending 元组也随之互换。这说明该字段不能被六项投影代表；不声称原 008 fixture 已观测到 pending 差异。Result 本身还保存完整 Definition。

直接改变 digest 的排序/去重会改变快照身份兼容边界，而不会自动规定如何保存原事件目录、pending、输入快照和版本。此次不实施这种变更。

## 3. 固定 PRD 与自有提案的原文依据及其限度

固定批准 PRD V0.6：93584 B、1255 LF，SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`，本次核实该固定副本。以下行号相对 `history/approved-prd-v0.6.md`。

| 原文位置 | 原文 | 本项能据此确认什么 |
| --- | --- | --- |
| FR-700，479 | “用户可以从基准项目或已有场景复制新场景，并配置初始状态、启用行为和规则、逐轮事件、资源与业务参数、观察指标及最大轮数。” | 输入不止同一场景名或版本标签，还包含实际事件和配置；没有规定复制后可沿用原快照身份 |
| FR-701，485 | “同一输入版本、配置和执行语义版本必须得到相同逐轮状态。” | 同输入的确定性要求；不能倒推结果子集相等就必须是同一完整输入 |
| FR-703，493 | “每次运行必须记录项目版本、输入快照、规则与行为版本、参数、事件、执行语义版本和逐轮状态。” | 原输入/依据必须可追溯；只看标签和指标不足以判定身份等价 |
| E.1，1024/1027 | “每个事件具有场景内唯一 ID；重复提交同一 ID 不创建新事件。”；“同一事件对同一行为至多触发一次。” | 支持重复提交的事件执行幂等，是 M 意见的实际相关依据；未明定含重复项的原 Definition 表示必须共享摘要/跨定义续跑身份 |
| E.1/E.2，1031/1042 | “再按事件输入序号升序，最后按事件 ID 升序执行”；“按输入序号和事件 ID 应用本轮全部事件。” | 序号是执行依据。008 保留序号的元组逆序不能与改变提交序号混为同一问题 |
| G.4，1230 | “独立重放恢复初始事件消费状态；从快照显式续跑时保留该快照的消费记录，不得重复建单。” | 规定重放/续跑消费边界；没有授予不同 Definition 表示间直接续跑的规则 |

本线 `history/product-candidate/docs/iterations/T07/integration-request.md` 也须保留其**提案身份**：第 1 行明确“待批准，私有适配口不作为公共契约”，不能将其升级成 T00 已批准公共合同。其第 16 行原文为：

> 重复事件同ID同内容去重，不同内容拒绝；显式续跑校验快照来自同一配置与输入，独立重放从原始消费开始。

第 18 行又要求完整带入并复验 project/version、engine/lock、scenario/input/rule/behavior/config/semantics，“不能只凭场景ID或页面当前选中项路由”。这些文本把事件处理幂等和续跑来源身份分别列出；并未写出两个 Definition 的等价关系。当前实现采取完整 Definition 摘要守卫，有明确可追踪的实现口径，但该提案不能代替 root 对规范化边界的正式决定。

既有测试文本也分开表达：`test_scenario_rounds.py:240–245` 检查追加同 ID 同内容事件后的 expected 投影及同 ID 异内容拒绝；没有断言 digest 相同或跨定义续跑可接受。230–236 的同一 d 续跑与完整运行 checkpoint 相等，及 V2 拒绝，均不是“只要同 V1 标签就共享快照”的保证。305–311 还明确复制新 scenario/input 身份后摘要不同。此处只读测试文本，不报告新测试通过。

**静态处置**：三组探针复用 P1/S1/V1/R1/B1 等标签，却实际改变了 events 完整值。未找到规定这些改变在续跑身份上必须被视为同一输入的明文；同样不把“没有明文”伪造为合同已明确禁止任何未来语义规范化。原事件幂等要求是真实约束，M 的契约可用性疑问继续登记。root 仍需明确：版本标签是否绑定完整原输入、规范化作用于何处、哪些目录/顺序/消费证据必须保留。未决定前不改摘要，不降作者 P2/P3，不接受其“非阻断/接线前再处置”作为已批准延期。

P3 的精度旁注：`canonical` 第 10–13 行已经 sort_keys=True，字段声明顺序本身不导致摘要改变；JSON 的 tuple/list 都表现为数组，且当前 Definition 对 events 要求 tuple。字段增删改名会影响完整值摘要，但是否应保持旧快照兼容是尚待定义的身份/迁移口径，不能仅凭 asdict 即认定现有源 bug。

## 4. 两处确定报告校正，原作者稿不动

| 原稿 | 校正旁注 | 依据和当前边界 |
| --- | --- | --- |
| Z R2 第 75 行将 IR-03 写为“项目/引擎/锁身份缺失” | IR-03 实为删除最高序号工单后复用历史 ID，混淆轨迹/去重 | `round-1/historical-issues.md:9`。`test_scenario_rounds.py:314–322` 的用例名及 W003/W004 断言对应此问题；357–364 的项目/引擎/锁身份用例是另一件事。只校正映射，不以静态文本新增运行关闭证据 |
| M R2 第 122 行指向 runner.py:2108–2111 | 实际函数/守卫为 runner.py:158–160（条件159、抛错160）；该文件共334行 | 固定源码原文：`checkpoint.definition_digest != definition.digest` 则抛 `Snapshot belongs to another input/configuration`。原稿保留，不在原文件改行号 |

两份报告原字节/SHA在 evidence-manifest.json 单列，写本旁注前后核验不变。

## 5. 分列保留事项：不合并、不抵消、不洗掉

### 5.1 原 M 新两项工程意见

| ID | 原等级 | 本旁注处置 |
| --- | --- | --- |
| R2-M-P2-1 | P2 | 原现象与新证据边界并列；rootDecision=null，未降级、未关闭、未接受延期；无确定源 bug 修复单 |
| R2-M-P3-1 | P3 | 原建议保留，纠正排序/表示相关表述；rootDecision=null，不自动采纳显式规范化字段或排序方案 |

### 5.2 原七项 P3 / 观察

| 原 ID | 原议题 | 保持状态 |
| --- | --- | --- |
| Z-P3-1 | initial_consumed 可显式声明未来事件 | 原登记/延期条件不变，未获其他 owner 承诺 |
| Z-P3-2 | 资源选中即完成 | 原 S1 最小语义记录不变，真实 T06 完成条件未验 |
| Z-P3-3 | 封存原行 hash 方法 | 原方法更正不变，不升级成读取/工程通过 |
| Z-P3-4 | ignored log/png 可追溯 | 原封存记录不变，不抵消全文读取或双流缺口 |
| M-F01 | 结果状态/失效原因标签 | 原登记不变，公共状态合同未决 |
| M-F02 | 续跑 phase=initial 语义 | 原登记不变，真实 T05 续跑未验 |
| M-F03 | 同实例动作序号连续性 | 原登记不变，不新增未经批准的1..k合同 |

原 seven-opinion-dispositions.json 不改；七项责任接收仍均 false。不能把相近的身份关键词当作已合并处置或其他 owner 已接单。

### 5.3 R1 NR01–05 / PROCESS_FAIL

| 原项 | 原流程问题 | 保持状态 |
| --- | --- | --- |
| NR-01 / P2 | fixture 全文缺项，M另缺私有源码 | 原事实/作者原文/Fail保留 |
| NR-02 / P2 | PRD与历史原日志通读不足 | 原事实/首失败保留，R2局部补足不回填R1 |
| NR-03 / P2 | Z被拒后包装执行，报告漏首错/拒绝 | 原拒绝→包装链保留，不与R2合规停止混同 |
| NR-04 / P2 | M固定review cwd原位probe | 原违规保留；后续真scratch成功不豁免 |
| NR-05 / P2 | M为定位收据向父项目发现性枚举 | 原范围越界保留，不推断他人正文被读 |

### 5.4 R2 当前读写/证据问题与运行未验

| 独立项 | 保留的原事实/门 |
| --- | --- |
| M授权面外写入及全局列举 / P2 | 45 B ledger占位写入、清理和全局assets列举；未披露。保原调用及脱敏说明，不因删除或作者PASS消除 |
| M全文声明和PASS证明不足 / P2 | 原Read链压缩缺口UNKNOWN；38项未独立重读却统一EOF；001–004原调用因果链不足。asset一致不能补证 |
| Z日志全文声明 / P2 | 六check日志选行，READONLY缺30字符及BrokenPipeError；不与其已披露G-1混为一项 |
| Z写面 / P2 | `/tmp/t07_r2_diffpaths.txt` 的tee越界与作者写面自述矛盾；本次不读/清理该实物 |
| Z IR-03映射 / P2 | 仅本旁注校正，原错误表格不能作为正确逐项关闭证据 |
| Z三必要验证UNVERIFIED | 自动拒绝未解除；现有独审未见绕行，本次不重跑；可选probe未跑不新增必跑门 |

依据为既有 independent-final-audit.md；没有新审查。当前两原 turn completed、完整双审门 PROCESS_FAIL / Pair 0、M fullRead gap UNKNOWN 与父能力/CI/远端/发布未验边界均不改变。

## 6. 交付和精确修改边界

仅新增本目录三件：本旁注、probe-output-comparison.json、evidence-manifest.json。源修复 proposal 为空，因为本包没有确认合同被违反的源 bug；不为凑三路径而提出未经定义的排序/去重改动。确定的报告错误以旁注交付，原作者稿和所有冻结材料不改。若 root 后续确定等价规则及具体违反点，才另起精确三自有源路径提案供签，本包不给后续执行授权。
