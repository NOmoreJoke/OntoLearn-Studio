# T05：规则批次复核的最小私有接口提案

本提案建议新增一个私有批量复核函数，在固定 `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb` 之外建立新候选，保留原 20 路径原件。函数内部重新编译一次、按原顺序重放一次给定 matches，并完整比对保存的批次。它不匹配真实图，不证明未提供匹配的穷尽性、图成员关系或 producer 授权。

当前仅完成静态提案准备；代码实施、I05 消费和原完整 T05 验收仍各需原来的实际依赖与门禁。原 Goal 不重建，Q6 不重问。当前状态仍以本线 `docs/reviews/T05/status.md` 为准。

## 1. 固定依据与确定的计费差异

授权原件为仓库外 `iteration-control/2026-10-21-weekly-release/T05-batch-revalidation-proposal-preparation.md`，2854 B，SHA-256 `1945dc6b79d696aafead283a43cac6fb09090c320cf8113d91aa7a051678ea54`。本提案只静态读取固定提交中的七模块；测试与夹具只取得路径、Git blob 和字节哈希元数据，不执行。绑定清单见 `docs/reviews/T05/rule-batch-revalidation-proposal/input-bindings.json`。未读取或改写主线独立 oracle。

固定 `rule_firing.py` 的路径为：

- `compile_rules`：一次 definitions/catalog 输入计费、每次 parse/发行及 spec 和 plan 编码；发行的 plan 与该 Budget 对象身份绑定。
- `evaluate_bound_batch`：一次 `_check_plan`，一次整批 `account_input(matches)`；完整执行每个 match，包括比较为 false 的 match，检查所有输入重复，再排序并生成全部 true firings、去重 facts；最后只编码一次 `(PROFILE, firings, facts)`。
- `check_firing_group`：每次先 `_check_plan`，再 `account_input(group)`，重新 `_one`，最后分别 `encode_output(expected)` 和 `encode_output(group)`。循环 N 组就有 N 次 plan 编码和 2N 份 group 输出编码；原输出还包含解析后的比较值、规则 source 和所有 head occurrences。
- `_walk` 对每个引用出现逐一计费，source 的别名、相同文段和重复 term 不因相同对象或内容免费。`fingerprint` 还单独收取 `max(1, len(data))` work。不能把“引用相同”用作抵扣理由。

因此，同一 child 内重新 `compile_rules` 后逐组调用现 API，并复用一份 `mechanism-budget/1`，与一次成功的批量执行没有相同成本上界。删 source、删比较、只验第一组、每组重新开默认池均不采纳。

### 确定的静态见证

取一条规则 r：`(?x, urn:p, "v") -> (?x, urn:q, "ok")`，catalog 仅声明 urn:p、urn:q 为 data properties；规则唯一 SourceRecord 的 text 为 40000 个 ASCII `a`，其余 source 字段为 None。两条 match 分别绑定 urn:s1、urn:s2，when 各为对应 ground triple，proof leaves 各为 f1、f2；无比较，所有 term 自身 source 为 None，默认 policy，revision/definition_digest 为 None。所有项用固定原生记录类和 tuple。

按固定 `_walk` 的 tag、字段名、类型分隔符和逐引用规则，纯字节算式给出：

| 项目                                                   |   字节 |
| ------------------------------------------------------ | -----: |
| fresh compile 的累计 input                             | 125370 |
| 原整批 evaluate 新增 input                             |  56671 |
| compile + evaluate input                               | 182041 |
| 原整批一次 output                                      |  82902 |
| fresh compile + 两次 plan 编码 + 两份 group 输入的下界 | 291430 |
| 两组 expected/group 双输出                             | 164428 |

`291430 > 262144`，且该下界尚未加入两次 `_one` 的解析/发行输入，故逐组复核必遇 input 资源失败；原执行的 input/output 字节均未触顶。`static-byte-census.py/json` 保留纯静态大小算式，不 import 或调用产品，不编码产品输出、不执行 parser/matcher/reasoner。它不证明 work 等其他计数已经实跑通过；真正新候选必须执行这一个完整见证，先证明旧 evaluate 成功，再证明旧逐组复核失败和新 API 成功。不得把这里的字节证明改写成已运行通过。

## 2. 精确私有 API 与表示前置

新增 `packages/engine/src/ontolearn_engine/quality/rule_revalidation.py`，直接导入固定类，不加入 package root 导出或新依赖：

```python
REVALIDATION_BUDGET_VERSION = "mechanism-revalidation-budget/1"


def check_firing_batch(
    definitions: tuple[RuleSpec, ...],
    catalog: Catalog,
    original_matches: tuple[BindingMatch, ...],
    saved: PreparedFiringBatch,
) -> bool:
    """Complete supplied-batch consistency; returns True or raises ProfileFailure."""
```

要求 exact 原生类/tuple，而非仅靠 annotations。调用者不传 CompiledPlan、digest seal、回调、比较器、matcher 或可重置预算。函数内部建立唯一 fresh plan；所有预期 ProfileValue 由原 `parse_value` 路径在同进程发行。保存比较证据中的 ProfileValue 也必须由同一模块身份的 `parse_value` 实际发行，且由保存对象持有强引用；直接构造同字段 ProfileValue、换 module alias 类、改字段后自行重算 hash 均失败。由 JSON/其他序列化形式恢复到这些类的方式属于 I05 的真实表示前置，本提案不创造 I05 DTO、公共 schema 或落盘格式。

`original_matches` 必须是原来调用 `evaluate_bound_batch` 时的完整原有序给定输入，包括比较为 false 的 matches，并保留每条 binding 的原顺序、全部 when、proof leaf 出现、TermInput/source。definitions 的顺序和 catalog 同样保持原样。它只是执行器当时给定输入，仍不是图全局完备证明。

这是本方案明确的额外输入要求，不是对 I05 已存在能力的陈述，也不是偷偷增加持久化承诺。可在原 child 内保留原 tuple 到“序列化保存值读回并复核”完成，从而无需承诺长期保存 false matches；如果目标是在 child 退出后再次复核，则必须由 I05 说明能否恢复相同原输入以及载体和额外大小/生命周期成本。缺失时明确拒绝启动该复核，不用保存 firings 冒充完整 original_matches，不重新调用图 matcher 代填。

### 为什么本次不选择仅由 true groups 恢复 matches

true groups 含 bindings/when/proof，足以逐项检查这些已保存 firings 的内部一致性，不需要 false matches 来证明图穷尽。但是固定 `_one` 在输出时会排序 binding pairs，原输入顺序不保留；从 groups 恢复再运行 `_resolve`，变量线性查找的收费顺序和长度可能改变。整批去重、匹配输入编码与排序成本也不同。不能据“逻辑上等价子集”直接推定 work/input 的原预算仍够。

仅 true groups 方案可以另行设计专用检查算法和严格新增成本界；它需要修改计费/执行辅助层或更广的独立界证明，不能在本次最小接口中用未经证明的倍数替代。当前选择保留原输入重放，以三个固定整批预算池得到可核验的成功蕴含；若 I05 无法满足原输入条件，先把此方案标为不可实施并交唯一 owner 协调，不能默增存储或改用未证明替代方案。

## 3. 一次调用的完整算法及失败边界

1. 仅做顶层 definitions、catalog、original_matches、saved 的 exact 类型与外层 tuple/批次数 guard；saved.firings/facts 的 tuple/数量、profile/payload/digest 的原生类型和常数时间 len 边界也在此处检查，payload 不超过 O、digest 长度 H=64、profile 长度 P。明确顶层 definitions≤100、original_matches≤1024、saved.firings≤F=1024，saved.facts≤旧 head_occurrences=16384；facts 不套用 firing 数 F。comparisons≤C=32 的 tuple/数量 guard 在第5步唯一遍历中完成，均不增加递归扫描。profile 相等比较先由 control 池付费。此步不递归遍历全部字符串、term、source 或记录字段；深层类型/长度交给 replay 与付费 `_walk`。所有 guard 不调用用户协议、迭代器、repr 或 property。
2. 在 **replay 池** 中 `compile_rules(definitions, catalog, replay)`，随后仅一次 `evaluate_bound_batch(plan, original_matches, replay)`。沿用原规则常量校验、全部比较（前项 false 后仍继续）、完整 head 构造、source、重复输入拒绝、排序和原子批次输出。不得改原函数或绕过 `_check_plan`。
3. 在 **saved-encoding 池** 中仅一次编码 `(PROFILE, saved.firings, saved.facts)`。固定 `_walk` 仍逐出现计费且只识别批准记录类；未识别类型、额外/遗漏 occurrence、变更 when/head index/source/basis/版本/顺序/原 lexical 均不能以 canonical bytes 相等通过。本步不另做逐组或递归 shape 预扫描：固定字段的 typed 编码与 fresh 完整字节相等共同约束内容。每组 exact PreparedFiring、comparisons exact tuple/数量及每项 exact ComparisonEvidence 的显式 guard 合并到第5步唯一计费遍历；不能在这里隐藏第二轮扫描。
4. 使用 **control 池** 在比较前付费，完整比较 fresh.payload 与 saved canonical bytes，再比较 saved canonical bytes 与 saved.payload，并比较 fresh.digest 与 saved.digest。policy 已在第一步比较。不得只比较 hash，不做 source 归一化，不去重 proof/groups/heads。
5. canonical bytes 已相等后，在 control 池每组/每比较各预扣1后，执行唯一一次组/比较遍历，完成上述 exact 类/tuple/数量 guard，再由 **saved-issuance 池** 对每项 left/right 分别调用原 `check_value`，拒绝同字段伪造实例、篡改和跨进程旧实例。计划不从 saved 提取；预期使用 fresh plan 自己的发行对象。遍历完整成功后才返回 True，不发布 fresh 或局部 saved 结果。

空成功批次可有非空 original_matches（全部 false）；也可原 matches 为空。两种都必须完整 fresh compile，不能借零 firings 跳过常量/闭包变量/头校验。遗漏、重复或额外 saved group/fact、后项 source/比较/head 被改、saved payload/digest 不一致、未发行 ProfileValue 都失败。若调用者提供另一份内部一致但缺少某些原 matches 的集合，函数不能发现“它不是原集合”，因此“确为原输入”是调用方集成验收义务；返回 True 不得宣称全局匹配穷尽或 producer 真实性。

错误沿用 ProfileFailure 的私有安全字段：resource 分类及安全 reason/location 保留；其他输入证据不一致、伪造/身份不符和意外异常统一为 INTERNAL_ERROR/internal（不回显 lexical/source/path/traceback）。不返回部分通过、跳过项或 repair 后对象。失败/取消如何映射正式 job 由其唯一 owner 的正式接口阶段决定。

## 4. 独立有界预算及成功蕴含证明

不改变 `PROFILE = OntoLearn-rule-comparison-profile/1`、固定比较语言、`mechanism-budget/1`、ProfileLimits 或 Budget；不允许任何旧 API 因此得到更大的旧身份预算。新模块仅组合三个**固定数量**的现有默认 Budget 实例和一个新私有 control 计数器，统一标识为 `mechanism-revalidation-budget/1`。它没有逐组 reset。

令默认旧限额为 I=262144 input bytes、O=262144 output bytes、W=16777216 work、F=1024 firings、C=32 comparisons/group、H=64 digest characters、P=len(PROFILE)。三个池分别只能消耗自己的旧默认限额，不能互借：

| 池             | 固定源操作                                                         | 合法原批次的上界依据                                                                                                                                                                                      |
| -------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| replay         | 原 compile + 原 evaluate，一次 plan 验证、一次原 matches、一次输出 | 与原执行输入/顺序/语义完全相同；操作序列及收费相同。原来用更紧 ProfileLimits 成功也必在默认上界内                                                                                                         |
| saved-encoding | 一次 encode_output((PROFILE, saved.firings, saved.facts))          | canonical 等值的合法保存结果与旧 evaluate 最后一份输出逐字段、逐出现相同，因此此段 work 不超过旧 W，output 不超过 O                                                                                       |
| saved-issuance | 所有保存 comparison operands 的 check_value                        | 与原 `_one -> compare_values -> check_value(left/right)` 的 true firing 检查逐项对应；false matches 和编译期常量检查只增加旧执行成本。该池的编码/哈希 work、input 是原执行相应收费的子集，分别不超过 W、I |

control 池采用可直接实现的独立计量约定：入口1单位覆盖固定数量的顶层 exact/len guard，不含递归扫描；第3步没有额外逐组预扫描。第5步唯一遍历每组1、每comparison1（含该次固定数量的native shape guard）；每次两个 bytes/str 的相等检查先付 `len(a)+len(b)+1`。外层 F、每组 C、payload O、digest H 和 profile P 在扫描前检查。两次 payload 比较合计至多 `4O+2`；digest 比较 `2H+1`；profile 比较 `2P+1`。故固定 control 上界为：

```text
K = 1 + F + F*C + 4*O + 2*H + 2*P + 4
whole work accounting ceiling = 3*W + K
whole input accounting ceiling = 2*I
whole output accounting ceiling = 2*O
```

逐一相加的 3W 不是经验倍数：分别是原 replay、单次保存编码、原 comparison 发行检查子集三个来源；K 的每项对应上述固定循环或比较。原 firings/head_occurrences/trace_items 上界只在 replay 池消耗，仍完整采用旧值。saved-encoding/issuance 池原有整数/临时整数/term/source/depth 限额仍保留；不放宽字段类型以换取通过。各池失败即整批失败，不能复位或挪用空余池。

成功蕴含的范围是：固定旧机制成功的同一 definitions/catalog/原有序 matches，其完整保存批次保持全部内容、在当前同模块进程正确重新发行比较值，并且保存载体已完整重建，那么上述三个池分别有旧成功执行或其中一段/子集的成本上界，control 有显式 K，故新复核不会仅因原逐组重复 plan/output 收费而拒绝。**这不是对任意被篡改数据的成功保证**；损坏输入可耗尽其独立池并以 resource 或 internal 整批失败。

本界是机制的 debit 单位和编码字节界，不是毫秒/内存/吞吐性能声明。三个 payload bytes（调用方 saved、fresh、保存 canonical）各受 O 上界；重放期间的 plan/输入/证据对象还须由 I05 真实载体及 child 整体资源门约束，不把 `3O` 说成进程内存上界。

## 5. 必要产品、测试和夹具路径

新代码阶段仅提议三条**新路径**；本次不创建这些产品文件：

1. `packages/engine/src/ontolearn_engine/quality/rule_revalidation.py`：上述私有 API、固定版本和三个池/control 实现。
2. `packages/engine/tests/test_quality_profile_revalidation.py`：真实固定模块单测、输入/结果完整集合和安全失败；不接真实图。
3. `tests/fixtures/quality/profile-revalidation-v1/cases.json`：独立手工给定的批次一致性/损坏预期、source 长度见证及版本元数据，不从 actual 输出生成 golden，不复制主线 oracle。

旧 20 路径逐项保留，不修改、不迁移、不覆写：

| 固定路径（quality/ 或 tests/fixtures/quality/ 下）                | 新候选处理                         |
| ----------------------------------------------------------------- | ---------------------------------- |
| `packages/engine/src/ontolearn_engine/quality/__init__.py`        | 原样；不新增 root 导出             |
| `packages/engine/src/ontolearn_engine/quality/rule_calendar.py`   | 原样                               |
| `packages/engine/src/ontolearn_engine/quality/rule_comparator.py` | 原样                               |
| `packages/engine/src/ontolearn_engine/quality/rule_firing.py`     | 原样；原 single-group API 完全保留 |
| `packages/engine/src/ontolearn_engine/quality/rule_numbers.py`    | 原样                               |
| `packages/engine/src/ontolearn_engine/quality/rule_profile.py`    | 原样；旧预算身份、类型、上下界不变 |
| `packages/engine/src/ontolearn_engine/quality/rule_terms.py`      | 原样；原发行校验不变               |
| `packages/engine/tests/test_quality_profile_calendar.py`          | 原样                               |
| `packages/engine/tests/test_quality_profile_comparator.py`        | 原样                               |
| `packages/engine/tests/test_quality_profile_firing.py`            | 原样                               |
| `packages/engine/tests/test_quality_profile_imports.py`           | 原样                               |
| `packages/engine/tests/test_quality_profile_limits.py`            | 原样                               |
| `packages/engine/tests/test_quality_profile_numbers.py`           | 原样                               |
| `packages/engine/tests/test_quality_profile_terms.py`             | 原样                               |
| `tests/fixtures/quality/profile-v1/calendar-oracles.json`         | 原样                               |
| `tests/fixtures/quality/profile-v1/comparison-matrix.json`        | 原样                               |
| `tests/fixtures/quality/profile-v1/firing-cases.json`             | 原样                               |
| `tests/fixtures/quality/profile-v1/lexical.json`                  | 原样                               |
| `tests/fixtures/quality/profile-v1/manifest.json`                 | 原样                               |
| `tests/fixtures/quality/profile-v1/numeric-oracles.json`          | 原样                               |

不改 import loader、依赖、锁文件、公开 route/contract、Store、worker、main/preload/UI、I05 C4 或 future4，不新造 matcher/reasoner。若新候选发现必须触碰旧 20 中任一路径，先回到总控给出具体必要性和更新后的精确候选，不把这份提案当隐含许可。

## 6. 必须实际执行的测试与验收

这里只列测试计划，未执行机制或产品测试：

- 执行前述 r/两 match/source40000 完整见证，断言旧 compile+evaluate 成功、旧同池逐组复核在固定资源上失败，新整批 API 成功；逐项检查输入、输出、trace 和 work usage。不将 byte 静态算式充作 work 实测。
- 多组、多规则、全部多 head occurrence、共享同一 source/同内容不同 source、多 proof leaf/重复 leaf、相同事实不同依据、词法不同值相等的完整保存结果；断言全部 firings/heads/proofs/source 保留，facts 仍为固定去重结果。
- bindings 原顺序不同于输出顺序，输入 matches 顺序反转、前/后 false matches、false 前项后有类型错误、零组/零匹配但常量或输出定义损坏：复核不得提前通过；分别保存并重放各自完整原输入，不拼凑预期。
- 后组比较值/result/operator/index、head triple/index、when/proof/basis、rule/source/revision/definition_digest/policy、group/fact 顺序和 occurrence 的单字段损坏；漏组、重复组、额外组、漏/额外事实、payload/digest 分别损坏，均整批失败，安全字段无原文。
- 同进程正确 parse 发行通过；直接构造同字段 ProfileValue、`object.__setattr__` 篡改后重算 digest、计划/值来自另一个模块身份或子进程序列化恢复后未经当前 parse 发行，均拒绝。跨进程只允许恢复原始 TermInput 后在当前批准模块重新 parse；弱引用被回收不能冒认发行身份。
- 三个池分别构造资源失败，control 的计量边界/提前长度拒绝；检查无每组 reset、无池间借额度、末组失败不返回已通过前缀；非法/超长类型对象不得触发用户回调。
- 对成功批次直接核对三池相应片段/子集费用和 K 各项；静态逐行审查新函数操作与本证明一一对应，若增加解析、额外编码/哈希、排序、扫描或复制，必须先更新来源界和版本。
- 在新候选上补必要独立审查及 `npm run check`；保留无 GUI/e2e/native/HMR 桌面限制。新增模块随现包规则实际包含才算包内可用；检查引擎打包输入是否自动覆盖新路径。若改变依赖/打包配置或 I05 引入真实新依赖，执行原适用包验证，在隔离环境补原生门，不把源码可 import 当成包内运行证明。

这些测试只验给定批次内部一致性，不能代替 I05 实际图解码、RDFS、匹配、真实保存载体或完整 FR-500–505/G.2。仅有准备文档不触发本轮产品 check。

## 7. 实施隔离、交付与精确待答

真正代码实施前由总控批准三路径及固定依赖，登记唯一 owner T05、隔离 worktree/feature 分支与核验 base/head。不得在冻结 1e3 候选上追加修改；原机制 20 blob、原全部证据包、主线独立 oracle 原件和其固定 hash 保留。新候选固定三条新产品路径和新证据，manifest 含原 20 的等值核验、Git blob/SHA-256/字节、版本、真实命令/exit、独审和预算对应表；审查期间不改候选。

拟新增实施证据目录为 `docs/reviews/T05/rule-batch-revalidation-implementation/`（本次不创建）。交 I05 的固定件包含新模块/测试/夹具 manifest、可复核 archive 和输入绑定、固定提交及批准的消费范围；实际 hash 在新候选冻结后给出，本提案不预填未来 hash。I05 只在另获批准的真实执行器阶段消费同一模块身份，不私改七模块或复制比较器，不回写旧 C4/future4。单 group API 留供原有调用者使用，但不得把“循环单组 + 默认执行池”标记为新批次复核方案。

实施前只需向真实 I05 owner 核清以下事实，不再询问用户 Q6，也不造另一套 DTO/oracle：

1. 真实保存表示是否保留所有 groups/比较/heads/来源及原 lexical；如何在当前同模块进程恢复 exact 记录类并正确 parse 发行比较值？恢复本身由哪一有界池负责、失败如何保持原子？
2. 执行期间完整原有序 BindingMatch 是否仍可用，包括 false matches、每条 bindings 顺序及 proof leaf occurrences？若只存 true groups，能否保留原 tuple 到保存读回复核结束；若要求 child 退出后复核，真实载体额外保存/恢复成本是否获准？这是待批准依赖，不能声称已存在。
3. 同一 definitions/catalog 原样输入由哪个真实不可变对象/ref 提供，是否已有批准的输入版本和 source 原件；它们与保存批次如何被真实 producer 绑定？本 API 不替代 producer/图成员鉴别。
4. I05 child 总体预算能否单独容纳这份新、有界复核阶段及保留的原输入，而不复用已消耗的执行池；实际来源/历史保存窗口是什么？不将三个机制池误称整个 child 资源证明。

答复和批准前可完成本提案静态独审及 docs 冻结；不启动 API 实现、真实执行或跨线消费。原指定双模型同候选审查、CI、正常合并和完整父验收门继续保留。

## 静态独审计费歧义处置

原22912B/9b3c稿和独审原报告封存于证据目录及原ZIP。仅澄清步骤1不做额外全结构递归预扫描，步骤3不另做第二次逐组/比较guard扫描；exact PreparedFiring/ComparisonEvidence及tuple数量检查合并到步骤5唯一计费循环。深层字段由原replay/付费typed编码覆盖。K的F与F×C各只对应这一遍，若实施另增扫描/排序/编码则必须重算来源界并另行审查；不将未知工作藏在guard中。原三池、K数值公式、额外原matches前置、三条拟产品路径和旧20不变边界均保留。
