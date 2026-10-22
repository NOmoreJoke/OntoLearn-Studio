# 九项 mutation 的固定供应源静态路径

本件只给出 `6891a5842302859a531cf82767c5a482417bc274` 实际 JSON 投影的修改位置、先决条件与须保持的原始见证，供实现时选择切入点。未导入或执行产品、测试、第三方库或 probe；未审查尚未冻结的 probe 实现，也未证明九项运行拒绝或费用、失败原子性。以下行号均属于固定供应 ref，而非新树工作副本。

唯一工作副本依赖是 `semantic_source_package_probe.py:82–86` 的九个名称。该赋值段按原行 LF 及末尾 LF 计 238 B，SHA-256 `592d463b014edeef4beb7aec20c072070cbd302b02aeb32e98a1422f4a3b6803`；它只是名称观察，不是候选产品身份。

## 固定输入与方法

已读本窗口授权、有限 root closure 原件及相关规则；AGENTS 实采仍为 15852 B / `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。供应源码均用 `git show 6891…:<path>` 读取，配合 stdlib AST/字节摘要，没有产品运行。

| `packages/engine/src/ontolearn_engine/` 下文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| `semantic_execution.py` | 35220 | `3ac496383349e3ddefea1672c27c88bacaf99f4436c22e96e1592393bac102f3` |
| `semantic_profile_restore.py` | 70203 | `1607d2968d2ba76ad0711be446fea7965641fb845226d0e683ac35e5d0f57243` |
| `semantic_profile_directsteps.py` | 46459 | `7927769077e363b23741f6dc78b7c0ec2ad00b7d3285f8403a190c0e00169b22` |
| `semantic_profile_production.py` | 19993 | `5c857470890bd810370ad877db930848ba08e80096c640037d39bea83c14a320` |

还静态交叉读取固定 `test_semantic_profile_directsteps.py`（42828 B / `7bd1b63fbdcaf70d0a78efa4432c1b6091f91d96758988a86b5764b5c5d4b708`）及 `test_semantic_profile_restore.py`（38135 B / `55fe7ed30642d2e1d75d7ffa4ac66a3144cb30f7fbf832b0762bf8e782f69c0b`）。这些既有断言是路径佐证，不是本次运行结果。

## 先固定 payload 形状与敌手边界

`semantic_execution.py:504–590` 的投影规则如下：dataclass 是平铺的 `{"recordType":"类名", …字段…}`，没有 `fields` 包装；tuple/list 都是 JSON 数组，没有 `items`；每一个整数都变成 `{"integerHex":"0x…"}`，不能直接写 JSON 数字；bytes 是 `{"encoding":"hex","bytes":"…"}`。readonly native view 的 `entries/items` 不能当 JSON 路径。

`semantic_execution.py:729–758` 的外层 payload 恰为七键：`format / implementation / reasoning / inputDigest / inputDigestDomain / sourceDigest / definitionsDigest`。fullview `/2` 的 reasoning 恰十五键，DAG `/3` 增加 `directSteps` 为十六键。每个 `mechanismBatches` child 恰十一键：`ruleId / definitionOrdinal / disabled / planDigest / batch / originalMatches / definitions / catalog / limits / budgetLimits / budgetUsage`（restore:69–107、945–1008）。数组顺序、`None` 与空数组必须区分。

必须从同次真实 producer/capture 取得原 `OriginalAllocation` 和 expectation，先完成未污染正例，再只深拷贝接收方的投影数据污染。原 computation/native result、原 bytes、原 capture 与 expectation 基体不得原地修改。尤其保留：

- allocation 的 `rule_ids`、`disabled_rule_ids`、所有 child 的槽顺序、`rule_id`、`definition_ordinal`、原 `ProfileLimits` 及预算版本；不能依污染 payload 再分配。
- 原 input/source preimage 与其 digest/domain；原 definitions/catalog 摘要和实际输入；implementation、schema/cache/budget/direct-budget 版本身份。不能从污染后的 wire 推回这些原始 premises。
- 原规则、Catalog、原 terms 的 lexical/datatype/language/source；不调用 reason、compile、evaluate 来替污染结果补齐或修复，不把 JSON 变成额外 oracle。

精确窗口 L36 要求 producer→compute→capture→restore→roots 共用本次真正签发的 expectation/allocation，不可按扰动结果另发 expectation。**本窗九项均须复用同一 expected/allocation 对象，连 payload/rows 两摘要也不得 rebind。** 因此要区分本窗可做的完整性检查和另域已有测试：

1. **原传输摘要保持不动**：任何 payload 字节改动都会先被 restore:1192–1193 的 A1 拒绝。这能验证原 capture 的完整性，不能声称已到达深层 DAG/child 检查。
2. **另域既有深层敌手测试**：固定测试的 `rebound`（directsteps test:229–240；restore test:258–264）只替换原 expectation 的 `payload_digest / rows_digest`，其余原见证及 allocation 保持。该测试事实有助于理解深层校验，但不构成本窗授权，**本窗禁止采用这种重绑**，也不能把这些旧测试当本 probe 的运行证据。接收 payload 的 canonical 编码及其每8192字符单cell rows 可按真实 wire 形状重建，但不得为其签发新 expected 摘要；若只改 payload 而保留原 rows，也须如实记录，不能声称满足 rows 一致性。

每次 restore 使用新的 RestoreLedger；DAG 还须新的 DirectStepsLedger。失败后的账本 failed/live 清零与禁止部分结果是可单独观察的性质，不能由静态路径或逻辑清零推导物理 H/GC 已释放。

## 九项可定位修改

以下 `last` 指非空数组的实际末项，不能以 `[-1]` 的 IndexError 充当产品拒绝。先决条件不成立应报 fixture 不满足，不能静默跳过或把未改动 payload 记为 mutation 成功。**本窗运行预期均先停 A1**。表中的 A3/A5/A9/DAG 等只是对应字段的静态纵深校验位置，不能声称本次九项执行到达这些位置；不得通过重绑来取得这种声明。

| mutation | 明确的接收方修改路径与类型 | 必须保留／拒绝依据 |
| --- | --- | --- |
| `payload-unknown-key` | payload 根新增唯一未知键，例如 `/mutationUnknown = true`。键必须原来不存在。 | 原七键全部保持；restore:1223 严格键集拒绝。不是在 `/reasoning` 新增键后仍称外层七键检查。 |
| `tail-source-tamper` | `/reasoning/termSources/last/value/source/reference` 改成不同的合法非空字符串；实际 `source` 须为非 None 的 `SourceRecord`。 | `value` 是扁平 `TermInput`，其 source 为 `recordType/reference/digest/revision/text` 五键（restore:429–451、741–749）。原 term、ordinal/span、input/source preimage 和 digest 不变；A9 将真实原记录与保存 occurrence 对照（1238–1253），source canonical bytes 另在1263–1266对照。若 fixture source 为 None，应明确选择非 None 的 fixture，或把该 None 换为完整合法 SourceRecord 并明确记录这种不同 mutation；不可盲索引或空操作。 |
| `tail-definition-tamper` | `/reasoning/definitions/last/revision` 改成不同合法字符串；`RuleSpec` 的实际键是 `rule_id/when/comparisons/heads/source/revision/definition_digest/policy` 加 `recordType`（475–502）。 | rule ID、顺序、原输入规则和 expected definitions digest 不变。静态纵深路径是全局定义与对应 child `definitions[0]` 的 A3 对照（879–881），另有 A13 原定义摘要；本窗保持原 expected，不能给攻击字节重签 definitions 或两项传输摘要。不能把原规则 heads 与计算 firing heads 混淆。 |
| `tail-limits-tamper` | `/reasoning/mechanismBatches/last/limits/work/integerHex` 改成不同、仍在该字段合法范围内的 canonical hex（例如原非零时取 `0x0`）；不得写 raw int。 | `limits` 是带 `recordType: ProfileLimits` 的记录，`budgetLimits` 同字段但无 tag（676–689）。原 allocation child.limits 一字不动。A3 在 decode limits 后立即对原 allocation 比较（884–888），然后才逐项核 budgetLimits。只改 limits 已是有效拒绝向量；若同步 budgetLimits，仍不能同步 allocation。不要声称验证的是费用上限放宽后的执行。 |
| `tail-child-tamper` | 一个确定、通用的身份向量是 `/reasoning/mechanismBatches/last/ruleId` 改为与原槽不同的合法字符串（原值 None 时也明确记为 None→字符串）。 | 原槽数、顺序、ordinal、disabled、allocation 保持；restore:866–878 静态有 A3 原槽对照。**本窗只可观察 A1，不证明末 child 的 16c 已调用。** 末槽16c失败需要另域专门反例及授权，不得靠本窗重绑获得或把此身份向量早拒绝称为末槽原子发布证明。disabled 槽的 batch/originalMatches 必须保持 None，不可当空 enabled batch。 |
| `dag-depth-plus-one` | `/reasoning/directSteps/steps/last/depth/integerHex` 改为原 depth+1 的 canonical hex。 | 仅用于 `/3` 且 steps 非空；ordinal、rule/result、两项 ordered premises、叶字典均不变。restore:914–943 先解投影；directsteps:1040–1043 要求 depth 等于 `1+max(parent depths)`。若原 depth 已达100000，+1先触发 decoder 上限，应如实注明，而非声称命中了递推等式。 |
| `dag-last-premise-forward` | 选择末 step 的一个 premise，整个替换成 `{"kind":"step","ordinal":{"integerHex":hex(本step.ordinal)}}`。 | 删除旧 leaf `reference`，不保留额外键；保另一 premise 与其顺序、result/rule/ordinal。self ordinal 在合法整数范围内却非 prior；directsteps:1022–1036 要求引用 `previous < pos`，因此可定位到前向／自引用拒绝，不依赖越界整数。需要至少一个 step，每 step 恰两项 premise。 |
| `leaf-rename-all` | 对 decoded projected JSON 的所有值递归，只将**精确等于**某实际原 leaf ID 的字符串替换成一个不同、同格式 `i05-proof:`+64小写hex 的 ID。 | 原 proof leaf triple、所有源 terms 和原 capture 不变。所有可见引用应同步替换以排除单纯悬空引用；不要 substring 替换，也不要把 prepared-batch 的 opaque hex 当文本替换。restore:1625–1634 从每个保存 triple 依原算法重算 SHA，故一致重命名仍被拒。directsteps test:1012–1046 原有同类静态佐证；它也只递归 JSON string，并未解码 opaque bytes。 |
| `head-occurrence-1023-15` | 对选定 `/reasoning/evidence/i`，只改 `firingIndex/integerHex="0x3ff"` 和 `headIndex/integerHex="0xf"`。 | 选真实 fixture：一 firing、两个 typed heads 的 indices `(0,1)`，aggregate evidence 两项；不能刚好实际存在 firing1023/head15。原 typed firingGroups、child batch.firings、头、result/inputs/basis/rule 不变。两数在 decoder 允许范围内（713–718），但 `_validate_explanation`:1639–1659 根据真实 typed firing/head 重建六字段逐项核对，A5拒假 occurrence。应在 `/3` 走此证明；原 test:1049–1077 正是该固定反例。 |

## leaf 完整可见引用清单与尾部注意事项

`leaf-rename-all` 至少覆盖下列真实 JSON 位置；是否存在取决于原 fixture，不能伪造补齐：

- `reasoning.proofLeaves[*].reference`；`reasoning.rdfsEvidence[*].proofLeaves[*]`。
- `reasoning.directSteps.steps[*].premises[*].reference`，只限 `kind=leaf`。
- `reasoning.evidence[*].basis[*]`。
- `reasoning.firingGroups[*].proof_leaves[*][*]` 与 `.basis[*]`。
- `reasoning.mechanismBatches[*].originalMatches[*].proof_leaves[*][*]`。
- `reasoning.mechanismBatches[*].batch.firings[*].proof_leaves[*][*]` 与 `.basis[*]`。

Proof 确为二维数组（restore:520–523），不是单层字符串数组。batch 的 `payload` 是带 encoding 的十六进制 bytes，`digest` 在659–671先独立核对；保持原 opaque payload/digest 能避免无关 A2 早拒绝。若要改变 opaque bytes，必须单列该敌手边界，不能悄悄重算 batch 或把新生成 batch 当原结果。

所有尾部向量应记录实际选中的数组索引与 before/after 值，证明确有一次变化且原数组顺序、长度未变。仅“末项改了”不能证明前面所有槽均走过16c：实际 restore 在所有前置检查后才进入1319–1341的逐槽唯一 `check_firing_batch`。同样，aggregate evidence 的假 indices 被 A5 拒绝，是完整 head occurrence 核验，不能据此宣称新规则链、权限或选中 Job 接线已完成。

## 结论与停止边界

九名称均有可静态定位的实际投影切入点；上表特别要求 source 非 None、数组非空、DAG `/3`、合法 integerHex 和已知真实 head fixture，避免路径异常或空操作冒充 restore 拒绝。**按本窗原对象复用门，九项污染只可声称真实签发摘要下的 A1 完整性拒绝；不构成深层 schema、DAG 或末槽16c原子性运行证明。** 后者需要另域已有证据或未来明确授权，不能在本窗另发 expected 达成。

本件没有产品候选通过结论、没有运行 Pass，也没有资源闭包／包运行／性能或物理释放结论。仅写此路径说明；等冻结候选后再按新授权独立审查。
