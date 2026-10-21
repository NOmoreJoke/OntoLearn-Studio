# T05：规则批次复核的最小私有接口提案

本提案建议新增一个私有批量复核函数，在固定 `1e3e0ee1d9d5b70f1f59233d0a3c64f6d85fd2cb` 之外建立新候选，保留原 20 路径原件。函数内部重新编译一次、按原顺序重放一次给定 matches，并完整比对保存的批次。它不匹配真实图，不证明未提供匹配的穷尽性、图成员关系或 producer 授权。

本次按 I05 实际分 child 载体事实修订，原 `c1a616bbc8fc699ad11cd73cbf663c3692515e5f` 文本 24357 B、SHA-256 `578032f78cd8571496c5709f18c7f5c02292db89cf316a52e3d2f49c61234bea` 已原样归档为 `proposal-revision-1-c1a-original.raw.md`，旧 ZIP/独审/Git 原件保留。原“每调用三个默认池”仅为历史提案，以下按可信原 child 限额的修订替代该入口和整次预算结论。

当前仅完成静态提案准备；代码实施、I05 消费和原完整 T05 验收仍各需原来的实际依赖与门禁。原 Goal 不重建，Q6 不重问。当前状态仍以本线 `docs/reviews/T05/status.md` 为准。

## 1. 固定依据与确定的计费差异

授权原件为仓库外 `iteration-control/2026-10-21-weekly-release/T05-batch-revalidation-proposal-preparation.md`，2854 B，SHA-256 `1945dc6b79d696aafead283a43cac6fb09090c320cf8113d91aa7a051678ea54`。本提案只静态读取固定提交中的七模块；测试与夹具只取得路径、Git blob 和字节哈希元数据，不执行。绑定清单见 `docs/reviews/T05/rule-batch-revalidation-proposal/input-bindings.json`。未读取或改写主线独立 oracle。

本次全文读取 I05 `profile-selected-carrier-facts.md`，实际 5316 B、SHA-256 `d7f128c22719561e75a737a7093a01d19132265f805f429eb9811cf7b74dcd47`，与总控给出的固定字节相等，原件见 `proposal-revision-1-I05-carrier-facts.raw.md`。这是 I05 对当前私有 P1 的事实答复：N≤100 分 child，原 W_i/I_i/O_i 等来自整次确定分池；当前 true 批次强引用可保本进程发行身份；controlled 含原有序全部 false/true matches，却未进入返回载体；保存 JSON 无 exact records 恢复/重发行器；正式 producer/有界持久载体和跨 child 保存窗口尚未由 T01 交付。本轮未读取或执行 I05 产品源码，不能把 owner 事实答复提升为本线运行验证。另全文读总控静态报告 `T05-controller-batch-revalidation-proposal-review.md`，17078 B、SHA-256 `a44ed73f2668a7684b55adc4cf94b861bb1e4fd243660069207588b03da66385`，原样归档为 `proposal-revision-1-controller-review.raw.md`；其§7要求的可信原 child 限额、ΣK_i、disabled 和独立 R 前置纳入本修订。总控随后已另行授权 I05 最小 temporary carrier 增量（同一原 tuple/defs/Catalog/limits/disabled 及预扣完整投影），尚非本提案已验证交付，亦不含恢复器、selected、长期 Store 或 T05 API 实施许可。

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

`291430 > 262144`，且该下界尚未加入两次 `_one` 的解析/发行输入，故逐组复核必遇 input 资源失败；原执行的 input/output 字节均未触顶。`static-byte-census.py/json` 保留纯静态大小算式，不 import 或调用产品，不编码产品输出、不执行 parser/matcher/reasoner。它不证明 work 等其他计数已经实跑通过；真正新候选必须执行这一个完整见证，先证明旧 evaluate 成功，再证明旧逐组复核失败和新 API 在同一可信原 child 限额下成功。不得把这里的字节证明改写成已运行通过。

## 2. 精确私有 API 与表示前置

新增 `packages/engine/src/ontolearn_engine/quality/rule_revalidation.py`，直接导入固定类，不加入 package root 导出或新依赖。未实现的旧提案预算名 `/1` 保留为历史；本次新入口明示 `/2`，避免把默认整池语义默改为分配池：

```python
REVALIDATION_BUDGET_VERSION = "mechanism-revalidation-budget/2"


def check_firing_batch(
    definitions: tuple[RuleSpec, ...],
    catalog: Catalog,
    original_matches: tuple[BindingMatch, ...],
    saved: PreparedFiringBatch | None,
    *,
    limits: ProfileLimits,
    disabled: bool,
) -> Literal["batch-consistent", "definition-only"]:
    """Revalidate one trusted child allocation, or raise safe ProfileFailure."""
```

`limits` 是可信集成调用方从**该次原 child 的确定分池**取得的 exact ProfileLimits，不从保存 JSON 接受自报上限、不回退到默认池，也不接受调用方回调、Budget 或任意 mapping。T05 在使用前逐字段验证 exact int（拒绝 bool）、0≤值≤旧 ProfileLimits 默认上界，并用固定字段表复制为新的冻结 ProfileLimits；后续三个池只使用这份值副本。入口的固定字段数量验证/复制属于 control 的入口1单位，不能趁此递归遍历输入或增加可变次数扫描。它只证明数值有限，**不能证明来源可信**：I05 必须由批准的分池算法/不可变生产上下文提供该值，验证 saved limits 与它完全一致；跨 child 时 T01 必须先核 producer/成功终态/项目快照/来源和定义绑定，才能调用。Python 参数或保存文件拥有相同字段不是授权凭据。

I05 还必须在调用之前约束 N≤100，以及所有 child（含 disabled、空定义、失败复核和重试）的分配账本；同一次复核不得给每个 child 重置为默认池。对重试不能从同一整次账本重新发一份额度。缺少可信原限额或整次分池闭合时拒绝该阶段，不能凭 typed 数值有限宣称整体有界。T05 此函数负责一次分配内的三个池；它不新造 I05/T01 分池或 producer 协议。

要求 exact 原生类/tuple，而非仅靠 annotations。调用者不传 CompiledPlan、digest seal、回调、比较器、matcher 或可重置预算。函数内部建立唯一 fresh plan；所有预期 ProfileValue 由原 `parse_value` 路径在同进程发行。保存比较证据中的 ProfileValue 也必须由同一模块身份的 `parse_value` 实际发行，且由保存对象持有强引用；直接构造同字段 ProfileValue、换 module alias 类、改字段后自行重算 hash 均失败。由 JSON/其他序列化形式恢复到这些类的方式属于 I05 的真实表示前置，本提案不创造 I05 DTO、公共 schema 或落盘格式。

`original_matches` 必须是原来调用 `evaluate_bound_batch` 时的完整原有序给定输入，包括比较为 false 的 matches，并保留每条 binding 的原顺序、全部 when、proof leaf 出现、TermInput/source。definitions 的顺序和 catalog 同样保持原样。它只是执行器当时给定输入，仍不是图全局完备证明。

I05 已答当前 controlled 未入返回载体，因此这项前置**尚未满足**。其最小申请是在每个 mechanismBatches 项保留实际传入 evaluate 的同一 originalMatches tuple、原 definitions/Catalog/division limits/disabled 状态及完整私有 JSON 投影；总控已另行精确授权该最小 temporary carrier 增量，**本轮没有收到其已实现/固定交付证据**，不能继续写为已交付。本提案不实施它，也不扩展为恢复器、selected、Store 或公共字段。原对象可在同 child 临时持有至读回复核完成；若要求 child 退出后仍可用，必须先由 T01 提供正式有界载体、成功 producer 绑定、读取权限、保存窗口及撤回/GC。保留/复制/编码与原 limits 的可信取得均要由 I05 在复核前独立预扣和计费，不藏进下述三池。缺失时停止 selected 读回阶段；不用 true firings 重建 original_matches，不重跑图补原 matches，也不把即时原对象复核冒充跨 child 保存读回。

### 为什么本次不选择仅由 true groups 恢复 matches

true groups 含 bindings/when/proof，足以逐项检查这些已保存 firings 的内部一致性，不需要 false matches 来证明图穷尽。但是固定 `_one` 在输出时会排序 binding pairs，原输入顺序不保留；从 groups 恢复再运行 `_resolve`，变量线性查找的收费顺序和长度可能改变。整批去重、匹配输入编码与排序成本也不同。不能据“逻辑上等价子集”直接推定 work/input 的原预算仍够。

仅 true groups 方案可以另行设计专用检查算法和严格新增成本界；它需要修改计费/执行辅助层或更广的独立界证明，不能在本次最小接口中用未经证明的倍数替代。当前选择保留原输入重放，以三个固定整批预算池得到可核验的成功蕴含；若 I05 无法满足原输入条件，先把此方案标为不可实施并交唯一 owner 协调，不能默增存储或改用未证明替代方案。

## 3. 一次调用的完整算法及失败边界

1. 先验证/复制可信有限 limits、disabled 的 exact bool 和固定顶层类型/常数时间 len 边界；definitions≤L_i.rules、original_matches≤L_i.bindings、saved.firings≤F_i、saved.facts≤L_i.head_occurrences，facts 不套 firing 数。非 None saved 要求 exact PreparedFiringBatch，firings/facts 为 exact tuple，profile/digest/payload 原生类型及长度先限 P/H/O_i；profile 相等检查先付 control。顶层 guard 不递归扫描字符串/source/记录字段，不调用用户迭代器、repr、property 或回调。若 saved 为 None 不伪造空批次。
2. 用三个独立 **Budget(copied_limits_i)** 的 replay 池 fresh compile 一次；batch 分支随后一次 evaluate_bound_batch，使用完整原有序 original_matches。保持原常量/闭包变量/全部比较、重复 match、head/source、原子输出行为；不改变旧 API。所有结果只能由当前 canonical 模块发行。
3. **disabled 分支**：original_matches 必须为空、saved 必须为 None；只在 replay 池完整有界 compile 原 definitions，不 evaluate、不制造 PreparedFiringBatch，返回固定 `definition-only`。它仅说明定义复核，不能记作 disabled 规则产出成功批次。**空定义分支**：definitions=()、matches=() 且生产本来无 batch 时同样只 compile，返回 definition-only；若生产确有空 PreparedFiringBatch，则走正常整批复核，不能凭空省略存在的 batch。非空 enabled definitions 且 saved=None 一律失败。原 disabled/无批次路径若从未做过有界 compile，旧“生产成功”本身不能推出该次 compile 成功；I05 必须明确补原定义校验和该 child 分配依据，失败则安全报告，不降低定义检查或伪造成功蕴含。
4. **batch 分支**：saved-encoding 池只编码一次 `(PROFILE, saved.firings, saved.facts)`；不另做逐组/深层预扫描。fixed typed `_walk` 按每出现收费，不删/归一化 source、proof、比较或 head。control 池在执行前支付两次完整 payload 字节相等比较、digest 相等比较；不只验 hash。
5. canonical bytes 相等后，control 池唯一一次逐组/逐比较遍历（各先扣1）检查 exact PreparedFiring、comparisons tuple/数量≤L_i.comparisons、exact ComparisonEvidence；saved-issuance 池对每项 left/right 调原 check_value。未发行、同字段伪造、篡改重 hash、跨模块/进程未重发行均失败。整批完整成功才返回 `batch-consistent`，不发布 fresh/局部 saved 输出。definition-only 路径不执行该遍历，不借未用池给其他 child。

空成功批次可有非空 original_matches（全部 false）；也可原 matches 为空，两者都完整 compile/evaluate。遗漏、重复或额外 saved group/fact、后项 source/比较/head 被改、payload/digest 不一致都整批失败。若调用方谎报原集合、把定义或 disabled 状态换成另一份内部一致输入，T05 不能证明其真实 producer/原匹配关系；该绑定必须由 I05/T01 在可信入口核验。两种返回值均不证明图成员或全局匹配穷尽，也不提升历史/unknown 为 current。

错误沿用 ProfileFailure 私有安全字段：resource 分类及安全 reason/location 保留；其他证据不一致、身份不符或意外异常统一 INTERNAL_ERROR/internal，不回显 lexical/source/path/traceback。未完整完成不得返回部分通过、repair 后对象或可发布结果。取消/失败的正式 job 映射仍由其唯一 owner 决定。

## 4. 按原 child 限额的独立预算与整次证明

固定 `PROFILE/1`、`mechanism-budget/1`、ProfileLimits 和 Budget 完全不变；只在新模块以三个固定数量的现有 Budget(copied_limits_i) 和新私有 control 计数器组成 `mechanism-revalidation-budget/2`。不放大旧身份，不按 group/重试 reset，不跨池或跨 child 借额度。c1a 的“三个默认池”不再是此修订的 API。

对 child i，可信原上限记为 I_i、O_i、W_i、F_i，比较结构上界 C=32（实际 guard 仍采用更紧的 L_i.comparisons），H=64、P=len(PROFILE)。原整数/临时整数、term/source、深度、规则/when/head/variables/bindings/trace 等结构和累计限制也原样用 L_i，不因传入预算而放宽。三个池的**逐 child**依据为：

| 池               | 固定源操作                                                             | 同一原成功执行的上界                                                                                                                                               |
| ---------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| replay_i         | 相同 definitions/catalog/原有序 matches，原 compile+原 evaluate 各一次 | 相同操作顺序、相同模块和 typed 编码，使用同一原限额值；因此 work≤W_i、input≤I_i、output≤O_i                                                                        |
| saved-encoding_i | 原 `encode_output((PROFILE, firings, facts))` 一次                     | 合法保存值逐字段/出现相同，是原 evaluate 最后输出编码那一段；work≤W_i、output≤O_i，不消费 input                                                                    |
| saved-issuance_i | 全部 true firing 保存 comparison operands 的原 check_value             | 与原 `_one -> compare_values -> check_value(left/right)` 逐项对应；原 false matches 和 compile 常量检查只增加旧成本，因此该子集 work≤W_i、input≤I_i，不消费 output |

saved-issuance 的字节相等前提先由完整 encoding/比较建立，再核发行身份；并非先按调用方提供的 domain/value 相信其内容。重发行 ProfileValue 本身是外部恢复成本，**不在该子集内**。三个池分别以原完整 L_i 为硬上限，不以“实际这次消耗很少”动态给出更高限额。

control_i 的计量约定：入口1覆盖固定数量顶层 guard/有限 limits 复制；第5步每组1、每 comparison1（含固定 native shape guard）；每次 bytes/str 相等比较先付 len(a)+len(b)+1。batch 的两次 payload 比较≤4O_i+2，digest≤2H+1，profile≤2P+1；无另一个隐藏的逐组/递归 guard 轮次。因此统一最坏上界为：

```text
K_i = 1 + F_i + F_i*C + 4*O_i + 2*H + 2*P + 4
per-child work <= 3*W_i + K_i
per-child input <= 2*I_i
per-child output <= 2*O_i
```

definition-only 路径只消费原 replay compile_i 和入口控制，不编码虚构 batch、不发行虚构比较，故仍落在该统一上界内；其成功蕴含以原定义已在 L_i 下有界 compile 成功为前提，不由“disabled 未执行”推得。

整次有 N≤100 个可信分配槽，disabled/空定义同样登记，失败已花的额度不退回重发。I05 必须先提供原确定分池和真实整次账本，证明 sum(W_i)≤W、sum(I_i)≤I、sum(O_i)≤O，及需要用到的 sum(F_i)≤F（W=16777216，I=O=262144，F=1024 是旧整次最大值）。随后才可推出：

```text
whole work <= 3*sum(W_i) + sum(K_i)
whole input <= 2*sum(I_i)
whole output <= 2*sum(O_i)
sum(K_i) <= N*(2*H + 2*P + 5) + (1+C)*sum(F_i) + 4*sum(O_i)
```

若还未证明 sum(F_i)≤F，则仅可使用 N≤100 且每 F_i≤1024 的显式较松上界，不能偷写为整次 F；在批准集成前必须由 I05 固定其实际分配。本式避免每 child 默认 3W 的 N 倍问题；N 项固定入口/digest/profile 开销明确保留，不能写成单 K。若调用方逐 child 都传默认 L，shape 验证可能合法，但整次原分池前提不成立，应在 I05 入口拒绝，不得据 T05 单次成功宣称整体有界。

成功蕴含严格限于：同一原成功 child 的输入、顺序、可信原 L_i、完整保存内容及当前正确重发行的比较值已经就绪，则三池分别对应原执行/单段/子集，不会因原逐组 plan/output 重复计费而误拒。更改 term/source/比较/head、错误 limits、截短原 matches 或借 disabled 跳过都不属于这个蕴含。恶意内容可 resource/internal 整批失败，必须有界且无前缀发布。

### 三池之外的真实恢复与全流程资源门

I05 事实中的“恢复 R_work≤原 W、R_input≤原 I，JSON≤8MiB/深度32/节点≤1M”只是其**待证明申请**，不是本提案已经证明的界。唯一 term 的 parse 可能对应原 compile/evaluate 某次 parse，但完整 TermInput/source 缓存键的生成、比较/散列、反复出现扫描、保存 ProfileValue 的所有 domain/value/language 对照、精确整数解码、JSON/typed bytes 恢复、原 matches 保留/复制以及载体/hash 均须另计；alias 不能免 T05 编码或 issuance 的每次费用。

I05 须给独立整次恢复 R 和读取/投影/摘要预算版本，证明其合法生产输出能完整恢复并逐字段对照；对每个 parse 唯一 term 的对应关系和缓存键/source 完整性逐项给静态来源界及实际 success→restore→recheck 测试。不能只说“有缓存”就给 R≤W；若此界不能成立，必须明确新有限上界/版本并经独审批准，或继续标记 selected 未完成。不得删 false matches/source/head/比较，不能静默用重算 domain/value/language 修复被改的保存字段，也不能用重新跑图填载体。

整次成本需写成上述 revalidation 界 **另加** 已证明的 restore/reparse/cache/traversal、原 matches 保留、carrier/hash/读回门，不能只报 3sum(W_i)。原 JSON+rows 最终8MiB及helper输入总池等由 I05 原门约束，额外投影新增 matches 是否仍容纳要实际证明。跨 child T01 尚需先验 producer 成功终态、项目/快照/作用域、实际 implementation 三字段、定义/原输入/source/载体摘要及访问权限，并正式规定窗口、撤回/GC；没有这些，不启动 selected 保存读回，不把短生命周期对象通过当已完成跨 child 可用。

该成本界是 debit 单位和编码字节界，不是毫秒/进程内存性能声明。每 child 三份 payload bytes 各受 O_i，但 retained plan、原 tuples、JSON/typed bytes、缓存和 child 存活窗口仍需 I05/T01 真实峰值/timeout/GC 门；不能把3sum(O_i)当总内存界。

## 5. 必要产品、测试和夹具路径

新代码阶段仅提议三条**新路径**；本次不创建这些产品文件：

1. `packages/engine/src/ontolearn_engine/quality/rule_revalidation.py`：上述按可信原 child ProfileLimits 的私有 API、固定 `/2` 版本、disabled/空定义分支和三个池/control 实现。
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

不改 import loader、依赖、锁文件、公开 route/contract、Store、worker、main/preload/UI、I05 C4 或 future4，不新造 matcher/reasoner。本次旧树20路径与1e3的字节等值证明保留；另一隔离树的IRI修复不在本轮读取/修改范围，不能把它登记为“旧20不变”。未来真正代码候选若绑定该修复后的机制，须由总控提供其独立批准固定ref，再核成本/兼容和精确采用清单，不能沿用本轮1e3等值证据冒充新基线不变。若新候选发现必须触碰旧 20 中任一路径，先回到总控给出具体必要性和更新后的精确候选，不把这份提案当隐含许可。

## 6. 必须实际执行的测试与验收

这里只列测试计划，未执行机制或产品测试：

- 执行前述 r/两 match/source40000 完整见证，断言旧 compile+evaluate 成功、旧同池逐组复核在固定资源上失败，新整批 API 成功；逐项检查输入、输出、trace 和 work usage。不将 byte 静态算式充作 work 实测。
- 多组、多规则、全部多 head occurrence、共享同一 source/同内容不同 source、多 proof leaf/重复 leaf、相同事实不同依据、词法不同值相等的完整保存结果；断言全部 firings/heads/proofs/source 保留，facts 仍为固定去重结果。
- bindings 原顺序不同于输出顺序，输入 matches 顺序反转、前/后 false matches、false 前项后有类型错误、零组/零匹配但常量或输出定义损坏：复核不得提前通过；分别保存并重放各自完整原输入，不拼凑预期。
- 后组比较值/result/operator/index、head triple/index、when/proof/basis、rule/source/revision/definition_digest/policy、group/fact 顺序和 occurrence 的单字段损坏；漏组、重复组、额外组、漏/额外事实、payload/digest 分别损坏，均整批失败，安全字段无原文。
- 同进程正确 parse 发行通过；直接构造同字段 ProfileValue、`object.__setattr__` 篡改后重算 digest、计划/值来自另一个模块身份或子进程序列化恢复后未经当前 parse 发行，均拒绝。跨进程只允许恢复原始 TermInput 后在当前批准模块重新 parse；弱引用被回收不能冒认发行身份。
- trusted child limits 原字段值逐一验证（bool/负值/超默认、缺限额、不可信 JSON 自报限额、外部可变对象/回调均拒），三个池使用独立复制值；多 child（含 N=100、分配余数、零 F_i、空定义/disabled）验证全局分池账本，故意每 child 默认重置必须在 I05 入口失败，不报告整次3W。
- 原成功 child 用比默认更紧的 I_i/O_i/W_i 运行后，在完全相同原限额下新 API 完整成功；bindings 顺序、false match/多头/source40000 见证必须覆盖；修改原限额或 controlled 次序不能悄悄仍归为同一次成功蕴含。
- disabled 无生产 batch 仅有界 compile 返回 definition-only；empty-definition 无 batch 与确有空 batch 分别验证，不凭空构造，enabled 非空且缺 batch 失败。未有原 disabled compile 成功依据的情形必须诚实保留不保证/安全失败。
- I05 实施后另验真实 originalMatches 保留/JSON roundtrip 及严格重发行，对保存 domain/value/language 的每一损坏都拒绝；缓存 alias/source差异/极长共同前缀、后项损坏、重放/restore/载体各自耗尽、末 child 失败均无部分 selected 输出。恢复 parse/cache/hash 的计费证明/真实测试不能由 T05 三池单测代替。
- 三个池分别构造资源失败，control 的计量边界/提前长度拒绝；检查无每组 reset、无池间借额度、末组失败不返回已通过前缀；非法/超长类型对象不得触发用户回调。
- 对成功批次直接核对三池相应片段/子集费用和 K 各项；静态逐行审查新函数操作与本证明一一对应，若增加解析、额外编码/哈希、排序、扫描或复制，必须先更新来源界和版本。
- 在新候选上补必要独立审查及 `npm run check`；保留无 GUI/e2e/native/HMR 桌面限制。新增模块随现包规则实际包含才算包内可用；检查引擎打包输入是否自动覆盖新路径。若改变依赖/打包配置或 I05 引入真实新依赖，执行原适用包验证，在隔离环境补原生门，不把源码可 import 当成包内运行证明。

这些测试只验给定批次内部一致性，不能代替 I05 实际图解码、RDFS、匹配、真实保存载体或完整 FR-500–505/G.2。仅有准备文档不触发本轮产品 check。

## 7. 实施隔离、交付与精确待答

真正代码实施前由总控批准三路径及固定依赖，登记唯一 owner T05、隔离 worktree/feature 分支与核验 base/head。不得在冻结 1e3 候选上追加修改；原机制 20 blob、原全部证据包、主线独立 oracle 原件和其固定 hash 保留。新候选固定三条新产品路径和新证据，manifest 含原 20 的等值核验、Git blob/SHA-256/字节、版本、真实命令/exit、独审和预算对应表；审查期间不改候选。

拟新增实施证据目录为 `docs/reviews/T05/rule-batch-revalidation-implementation/`（本次不创建）。交 I05 的固定件包含新模块/测试/夹具 manifest、可复核 archive 和输入绑定、固定提交及批准的消费范围；实际 hash 在新候选冻结后给出，本提案不预填未来 hash。I05 只在另获批准的真实执行器阶段消费同一模块身份，不私改七模块或复制比较器，不回写旧 C4/future4。单 group API 留供原有调用者使用，但不得把“循环单组 + 默认执行池”标记为新批次复核方案。

I05 已给本轮真实表示答复，不再把“是否保存 controlled/有无恢复器”列作未知：目前均缺，现有强引用仅够本进程。仍需由 owner 交付的精确前置为：

1. I05 固定 originalMatches/原 spec/Catalog/limits/disabled 的真实私有载体增量，证明原有序 true/false matches 及所有 source/proof 不丢失，新增保留/投影处预扣及最终 JSON+rows 门成立。
2. I05 固定原 child limits 可信取得、整次 N/分配算法/账本和重试规则，与保存字段相等验证；含 disabled/空定义 compile-only 成本依据。T05 数值 shape guard 不能替代这份来源。
3. I05 固定严格 exact records 恢复/重新 parse/保存字段全对照与独立 R/缓存/hash 界，给完整合法结果 success→restore→recheck 的来源证明和真实测试；R≤原W/I尚未证明，必要时申请新有限版本，不隐藏成本。
4. T01 实际提供成功 producer/不可变输入及来源绑定、有界载体、作用域/implementation/状态校验、跨 child 保存窗口与撤回GC，再允许 selected 读回；不由本提案或数学内部一致性代办。

答复和批准前可完成本提案静态独审及 docs 冻结；不启动 API 实现、真实执行或跨线消费。原指定双模型同候选审查、CI、正常合并和完整父验收门继续保留。

## 静态独审计费歧义处置

原22912B/9b3c稿和独审原报告封存于证据目录及原ZIP。仅澄清步骤1不做额外全结构递归预扫描，步骤3不另做第二次逐组/比较guard扫描；exact PreparedFiring/ComparisonEvidence及tuple数量检查合并到步骤5唯一计费循环。深层字段由原replay/付费typed编码覆盖。K的F与F×C各只对应这一遍，若实施另增扫描/排序/编码则必须重算来源界并另行审查；不将未知工作藏在guard中。这是 c1a 历史处置；本次保持这一次计费遍历，按可信 L_i 和 K_i 修订三池入口及整次合计。额外原matches前置、三条拟产品路径和旧20不变边界保留。
