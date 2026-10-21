# I05 strict restore 实现独立 schema / 重新发行 / 原子性审查

结论：**不通过，1 项 P2 阻断 strict 前门合同。** 固定实现会先调用 `OriginalAllocation.rule_ids` 内嵌外来对象的 `__len__` / `__iter__`，随后才拒绝非 exact tuple。父审已在真实 capture → 实际 restore 入口复现；本审另以固定源码 AST 独立复现对应分支。除该问题，本次范围内未发现另一个可复现的 schema、PV 修复接受、分池数值或部分事实发布问题。

这是实际实现审查，不沿用方案通过结论。没有修改源码、测试、68 项只读输入、环境或 AGENTS；只写本目录审查与审计文件。未提交、切分支或操作 Goal。

## 固定对象及依据

- 根目录：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-restore`
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- 代码 ref：`bbd79c3cff88e8fef348a9c4dcb6981ab5e3cb47`
- 测试 ref：`b301c3cdb348c08c6d10f1ac4e11666ec9bbd39b`
- 已读本 review 根授权原件、`approved-plan.md.raw`、固定输入 manifest、当前完整 AGENTS、`developer-common-instructions.md.raw`（含完整第九节及无桌面规则）。当前 AGENTS SHA-256：`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。
- 新核心两模块均从 `git show <fixed-ref>:<path>` 完整逐段读取。需要的原 producer、projection、canonical 类、16c API 来源属于只读采用项；审计确认其固定 ref 和当前字节均匹配批准 manifest 的全部 **68 项**。

| 固定路径 | 字节 | SHA-256 |
| --- | ---: | --- |
| `packages/engine/src/ontolearn_engine/semantic_profile_restore.py` | 47127 | `8a09474ee3f5c71b9b4205df8ee590106bad34ac6ad01c06ee9f310c84487889` |
| `packages/engine/src/ontolearn_engine/semantic_profile_restore_budget.py` | 37212 | `95b170ab99220d8d602d87a321bae481774806dc2bc11b760b4933e866f51c16` |

上表哈希也在 `audit.json`，审查结束时当前核心与固定字节相同。测试按其固定 ref 读取；不把主树未提交测试状态当作版本。

## 阻断问题 S1

**[P2] 在 exact tuple 核型之前调用内嵌 `rule_ids` 的对象协议。**

- 位置：`semantic_profile_restore.py:837`，紧接着 `:838`；真正的 exact tuple 门位于稍后调用的 `allocation_order()` 的 `:716`，调用点 `:841`。入口 `:1153` 只检查 `OriginalAllocation` 外层 exact class，`:1163` 只早检 `children`。
- 触发：保持原 payload/rows、原 expected 及摘要不变，仅使用 `dataclasses.replace(original_allocation, rule_ids=Bomb())`。`Bomb.__len__` 可执行副作用再返回原规则数量，`Bomb.__iter__` 可执行副作用再提供相同规则 ID。外层仍是 exact `OriginalAllocation`。
- 实际行为：恢复器在 `reasoning()` 中先执行 `len(self.allocation.rule_ids)`，随后 `zip(definitions, self.allocation.rule_ids, strict=True)`。两种外来协议均已经执行，才由 `allocation_order()` 拒绝。
- 影响：违反私有入口“不接收用户回调”及所有 nested 字段先 exact 核型再操作的 strict 合同。最终安全拒绝不能撤销已发生的外部副作用；若回调阻塞或无限执行，恢复账本也不能给其施加所声明的操作界。本问题不意味着 saved bytes 自身能携带 Python 回调，也不声称能伪造原生产来源或获得恢复成功。
- 依据：批准方案第 2 节要求 exact 私有上下文且不接收用户回调，第 3 节要求按位置严格 schema；已有测试也明确声称 strict entry 不调用 foreign object protocols，但只覆盖外层 foreign 对象。
- 真实入口证据：父审在主树自身隔离运行中执行真实 `capture_case()`，再构造 exact `OriginalAllocation` 的 foreign `rule_ids` 后调用实际 `restore_profile_batches`；`runs/05-schema-callback-probe.json` 记录 `callbacks=["len","iter"]`，随后 `RestoreFailure / RESTORE_INPUT_INVALID / input`，绑定核心 SHA 与上表一致。本审已全文读回该原件并将其内容、文件摘要纳入 `audit.json`。该真实入口探针由父审执行，未冒称本子 agent 重跑完整引擎。
- 独立分支证据：`audit.py.raw`（运行时原名 `audit.py`）使用标准库从固定 Git 源 AST 原样抽取 `_Decoder`、`OriginalAllocation`、Catalog 及其必要常量，执行原 `reasoning()` / `allocation_order()`，仅把账本替换为计数记录器。Python 3.12.14 实测得到 `callbacks_before_rejection=["__len__","__iter__"]`，随后 A3/input 拒绝。此证据是对应实现分支探针，不冒充完整生产测试。
- 修复建议：将 `rule_ids` exact tuple、最多 100 项，以及 `disabled_rule_ids` exact tuple 的基础形状门提前到入口或 `_check_expectation()`，至少保证在第 837 行之前完成；仍保留后面的成员、唯一性、次序和分池对照。不要用 tuple 转换来“修复” foreign iterable。
- 必要回归：exact `OriginalAllocation` 内嵌具有副作用 `__len__` / `__iter__` 的对象，以及 tuple 派生类；调用后副作用计数必须为零、原 expected/hash 保持不变、账本 failed、无部分结果。继续保留现有合法原分池与 false/true 顺序检查。

测试盲点的精确位置：`test_semantic_profile_restore_limits.py:209` 的 foreign 协议测试只污染 outer expected/allocation/blob/ledger；`:237` 的 exact 类测试包含外层派生类与 `ProfileLimits.work=True`，未覆盖 exact 容器中的外来 `rule_ids`。该盲点归入 S1，不另重复计问题。

## 实现逐项审查结果

以下“符合”指固定源码与已批准本阶段合同的静态对应关系，不把它表述为完整运行或生产证据。整次逐操作预算及 live tickets 数学证明由另一位独立 agent 负责，本报告不替代其结论。

| 项目 | 实际代码核对 | 判断与边界 |
| --- | --- | --- |
| wire 前门 | budget `:474–740`：exact bytes、严格 UTF8、受限词法 pass 后 build pass、35 层、节点门、固定键表、重复键、32 字段门；禁止原生 JSON number/NaN/Infinity、孤立 surrogate。main `:991–1002` 与 `:1020–1055` 再按位置核 schema 并 canonical 逐字对照。 | 符合；无 object_hook、pickle、动态 import 或用户构造器入口。S1 是 native 捕获上下文的独立缺口。 |
| 字段及 native classes | main `:276–469`、`:507–704`：完整 SourceRecord 4 项、TermInput 5 项、Variable、Triple、Comparison、RuleSpec 8 项、Catalog 3 项、BindingMatch 4 项、完整 Number/Calendar，以及固定 17 L / 6 usage。`object()` 核字段数、全部固定字段、固定 tag；构造器来自代码白名单。 | 符合；`InputLocation` 无成功载体位置，不能借合法 tag 进入。Variable 只放模板 subject/object 与 Comparison operand；ground triple 三项均 TermInput。 |
| tuple/list 恢复 | `collect()` `:296–306` 默认 tuple；only native_list 用于 rdfs/rules/warnings/evidence/rdfsEvidence 及其 inputs/basis；evidence result、basis refs、proof rows、head/comparison、termSources/span 保持各自原类型。 | 与原 `semantic.py:1090–1118` 和 producer projection 对照一致；不靠 JSON array 自带容器身份。 |
| source 各位置 | SourceRecord 所有字段均 nullable str 且 65536 UTF8 门 `:346–351`；RuleSpec 独立 revision/definition_digest 仍是原 term 门 `:416–417`。Turtle caller reference/revision 另在 `:973–974` 核 16384，不误套全部 source 字段。 | 符合，None 与空串保留；40000 source 字段不会被通用 term 门误拒。 |
| complete matches / firings | `:442–450` 完整恢复每个 BindingMatch；`:812–813` 保留全部 ordered originals，未从 true firings 逆造；`:530–570` 保留所有 comparison/head occurrence/index/result/basis 与 rule metadata。 | 符合；false match 仍交给 16c replay。完整原生产顺序由原 expected payload 摘要绑定。 |
| 重复 firing 投影 | `:850–865` 逐位置完整对照 top `firingGroups` 与所有 child batch firings 顺序 concatenate；`_same()` `:225–260` 先 exact type 再固定字段递归比较。 | 符合；没有只选一个重复位置、忽略 basis/source 或把 head 当 facts 集合去重。 |
| PV 不修复 | `:471–505` 将保存 PV 解为 descriptor，只以 canonical `parse_value` 新发行；无直接 ProfileValue 构造；每一次 occurrence 都完整 `_same(term/domain/value/language)`。Number 三字段及 Calendar 四字段和 second Number 全比较。 | 符合；negative_zero、language raw/normalized、domain、最后字段都不能靠数值等价或 canonical 修复掩盖。 |
| 完整 cache key | budget `:864–921`：固定 8B header+source 存在位+8 nullable 字段 marker/4B length/UTF8，framing=49B；None 与空串、source=None 与空 SourceRecord、plain 与 xsd:string、raw language 大小写均区分。`:1036–1088` trie 查找用完整字节边；hash 仅审计。 | 符合；cache 每 child 新建，fresh PV 强引用至全部 API 完成；源码未引用 alias 模块或 pickle。 |
| witness 与同次捕获 | `:959–1001` 核原四个 wire/witness 摘要及 payload identity；Turtle `:967–984` 必须 source witness、原 raw UTF8、digest/text 门；structured `:1009–1042` 按 ordinal 三项重建输入并逐项核 source tuple 和 canonical 前像。 | 符合纯机制边界。不能由本入口验证调用者真的独立捕获；这是明确可信前提。空图及大 Turtle 文本仍要求外部前像。 |
| definitions/Catalog/aggregate | `:1028–1046` 重算 definitions 与 Catalog 投影摘要；`:1020–1028` result→source→definitions 共用原 projection 实例，structured records 另用实例；全部 metadata strict/canonical/hash-bound。 | 符合。未额外 compile 补 planDigest，未重算图结论/graphBudget，receipt 明示 `aggregate_recomputed=False`。 |
| 原 allocator | `:710–772` 从实际 `semantic._PROFILE_POOLS` 做 Unicode rule-ID 稳定排序、保留 ordinal、每池 divmod；每 child 17 字段 exact int 等于其位置应领值，核 captured L 及 saved L/budgetLimits。disabled 仍占槽。 | 数值与原 `semantic.py:915–922` 一致；Σfirings=1024，非每 child 各发整池。S1 需先补容器门，但不影响此段合法输入数值公式。 |
| disabled / 真空 batch | `:807–813` disabled 必须 originals=None/batch=None；仅 `:1068` 向 definition-only 参数显式映射 originals=()。enabled 包括 dummy child 和真实无匹配均必须保存实际 batch。 | 与 16c `rule_revalidation.py:140–166` 一致，不伪造 disabled 空 batch，也不跳过真实空 batch replay。 |
| 先全校验后 API | 所有解码/PV/source/rows/canonical 对照完成于 `:1055`；唯一 16c 调用位于 `:1061–1072` 顺序循环，每 slot 一次、limits 使用原 captured child L；slot start/complete 记账。 | 符合；此代码没有 reason/matcher replay、外部写入、yield 或回调发布前缀。 |
| 原子发布与异常 | `_restore()` 只在所有 child 成功后返回内部 tuple；public return 在 `:1204–1213`。`except` 新建有限错误，退出 except 后才 raise，避免原内部 traceback 作为异常链保留；finally `drop()` 清 cache/parse refs/child dict，再 cleanup/finish。 | 所检查的普通异常/末槽 ProfileFailure 路径符合全失败行为。不是 Store 事务/worker 终态证明，也不声称 Python 的 traceback 对象本身不存在。 |
| 临时清理 | decoder `:891–896`；budget cache `:1090–1116` 逐 node 清 value/key/children/next，再释放自身持有，不需要耗尽域再扣 work；释放 key 的 finally 在 main `:497–500`。 | 静态未见因合法资源拒绝遗留的 cache 强引用；live 账本模型本身及 opaque 峰值归预算独审。 |

## 所有 native 捕获嵌套字段的前门复查

应父审追问，本审逐项检查同类路径，结果如下：

- `RestoreExpectation`：schema/budget/cache 三版本均先 exact str；input_domain 先 exact str；六个摘要先 `string()` exact str 再长度/字符；implementation 先 exact tuple、每 pair 先 exact tuple、key 先 exact str，value 经 exact str 门；两前像先 exact bytes 再长度/hash/decode。未发现 foreign `len` / iteration / equality 先执行路径。
- `OriginalAllocation.children`：入口先 exact tuple 后 len；每 child 先 exact ChildAllocation 后读取 limits，再要求 exact ProfileLimits。`child.rule_id`、ordinal 使用 `_same()` 先 exact type，不触发外来比较。17 个 L 字段先 exact int 再数值比较。
- `OriginalAllocation.budget_version`：先 exact str 再比较。`disabled_rule_ids`：先 exact tuple 后长度/迭代，成员先 `string()` exact str 再查找/比较。未发现同类缺口。
- `OriginalAllocation.rule_ids`：只有本报告 S1；tuple 成员与 spec.rule_id 的 `_same()` 自身先做 type 检查，问题发生在容器早期 `len` / `zip`。
- 这里审查的是正常构造的私有 ledger 及提供给公开私有入口的捕获字段，不把主动篡改任意 Python 模块全局/ledger 私有内部状态当作本纯函数能认证的安全边界。

## 测试审查、实际验证与限制

本审读取固定 b301 两个测试文件，检查真实 `capture_case()` 在原 fixture 固定后只观察一次 `semantic.reason`，然后让原完整 execute projection 完成；receiver 使用 `subprocess.Popen([sys.executable, test_path, "--restore-child"])` 启动新解释器，仅传 bytes/捕获数据，断言初始 `_ISSUED_VALUES` 空，并把 reason/matcher 设为禁止。完整 child native signature 保留 exact tuple/list、全部 fields、false/true tuple 与每个调用的原 L。

已读的测试覆盖 source 四字段 40000、重复 source、全部 PV domains、Number/Calendar 末字段、disabled/两个实际空状态、空图/大 Turtle witness、false 后类型错误、strict wire 边界、原 expected 全 leaf 污染拒绝、重绑 wire 摘要触达内部 PV/schema、末 rows 尾片、alias/pickle、原分池1/2/100、各计量域 exact/差1、末 child checker 失败、trie 256 分支和人工审计 hash 碰撞。**N=100 若原生产已 resource failure，会明确记录负例，不是成功恢复证据。** 不把参数化总数当分支覆盖证明。

false/true 置换且敌手重绑 wire 摘要后，16c 可能得到机制等价输入，这是已批准的“不认证原来源”边界，不作为产品缺陷；保持原 expected 不变时污染仍由原 payload 摘要拒绝。测试 b301 对该前提的明确说明正确，没有放松原完整保存要求。

实际执行：

1. 本 agent 执行 `/opt/homebrew/bin/python3.12 .../schema-review/audit.py`：两核心及两固定测试 AST parse 通过，核心固定哈希一致，68 项当前/固定输入均匹配 manifest，独立 AST 分支探针复现 S1。没有导入共享 `.venv` 或新增依赖。
2. 父审执行真实入口 S1 探针，原件已读回并绑定。本报告没有把它冒称为子 agent 自身的完整运行。
3. 父审提供首跑 `runs/04-*` 的 134 pass / 5 fail 原件及 b301 writer 独立 139 pass 信息；本 agent没有重跑完整139例，不用旧首跑或转述替代最终完整 check。
4. 仅本目录 `report.md` / `audit.json` 的 `prettier --check` 通过；不改归档原件或其他文档格式。

归档补记：为避免全仓 Ruff 把诊断探针当作 active Python 源，审查收尾后仅将 `audit.py` 改名为 `audit.py.raw`，原始与改名后均为 **7030B / SHA-256 `75df916376fde70311ef795959d94ac6c6d875d54395ea75e3f9e26e611503d4`**。原字节未改，历史运行命令及结果保持原样；此次没有重跑探针或读取实现 delta。前后路径及摘要记录见 `archive-receipt.json`。

未执行 GUI/Electron/e2e/native/HMR/CUA/Keychain、模型、付费操作、push/PR/merge。未运行全仓 `npm run check` / `verify:sources`，它们仍由实施 owner 对最终候选执行。未证明全部 restore R 上界、RSS/CPU容量、正式 selected/producer/Store/worker/权限/生命周期、目标平台及上线。指定双方新审和 CI 门未被本审替代。

## 修后复核出口

修复 S1 后生成新固定候选，新增内嵌 foreign 协议零调用回归，再运行相应 restore 测试及任务要求的最终检查。必须复核新核心/测试 SHA、68 项保护源、原 expected 不变污染拒绝、合法 capture 原 L 和末 child 全失败行为。此报告的“不通过”固定针对 bbd，不随后续 WIP 自动变为通过。
