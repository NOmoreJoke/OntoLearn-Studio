# 6c1eec4 来源、schema 与生命周期 delta 复审

结论：固定 `6c1eec41091a997f898cb448bfc7d4000c154307` 的本次 delta，在来源捕获、schema 保真、旧 facade/测试兼容和受控 Exception 清理范围有限通过，未确认新增阻断。维持首审对这些范围的结论；预算两项修复的充分性由独立预算审查判断，本报告不代签。完整 npm check 由 root 执行，此处不提前记为通过；不表示正式 T01 Job/Store/origin、owned worker、selected 或整个 I05 成功。

## 版本、输入与保护

- 旧候选：`f677d8a3a642ef7ac7bf389218d43564762bcd9a`；新候选：`6c1eec41091a997f898cb448bfc7d4000c154307`。
- adoption：`e4460763890cf9550f359395df83260d75fe2e0a`；base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 唯一树仍为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration`，职责和最新授权沿首审，未扩展写权或运行范围。
- 逐项核 `candidate-6c1eec4.json` 全部 139 项当前字节=固定 Git=声明 bytes/SHA；130 非 writer 等 adoption；f677→6c 恰有下列四路径。身份清单为 `delta-6c1eec4-inputs.json`。
- 逐项复核首审 `write-lock.json` 所列报告、manifest、AST、raw probe、argv 元数据及双流全部原 bytes/SHA，未修改。首审报告仍为 16647B/SHA `02d036cd801abd0c59ffee92a613fde270973c72516cf79a9479281be747bb6d`。

| 实际改变路径（共同前缀 packages/engine/）           | 新 bytes | 新 SHA-256                                                         |
| --------------------------------------------------- | -------: | ------------------------------------------------------------------ |
| src/ontolearn_engine/semantic_profile_input.py      |    40378 | `f4d76b68e6bd5f27d4e1c0ee7b26435117b1dd762a4b2a16503d41afd1841f74` |
| src/ontolearn_engine/semantic_profile_production.py |    10975 | `00822bb6851a25f8ca6c47cba73d22483b10694161a2732337e1a0a2bdb56b97` |
| tests/test_semantic_profile_input.py                |    12085 | `eaceece4cc903ee6b46abcad809a02a8cebb376573ad801b4175d4fa59fb70cc` |
| tests/test_semantic_profile_production.py           |    11705 | `ad116e7e66cdad97c49e6fdf772042bf188d91f4ff53dbfdbb575ac6f7b04cb0` |

## 实际 delta 与必要上下文

全文读取四路径的固定 Git diff，并对照首审已读的完整实现及本次相关上下文。以下行号均指新 ref，源码共同前缀为 `packages/engine/src/ontolearn_engine/`。

1. `semantic_profile_input.py:74–97` 的 ledger constructor 不再建立 checked list/tuple；保留调用者的 exact tuple。最多五项，每项先 exact tuple2/name exact str 且固定域/value exact int，之前成员已通过同样门后才在有界 previous loop 比较。引用原 immutable tuple 不引入新可变别名或 foreign 协议执行路径；重复域仍拒绝，没有放松类型或 lower-only 语义。
2. `input.py:99–128` 在建立 caps/used/live/peaks/stage arrays 前先判实际 objects 控制下限是否至少 64；live/peaks 初值直接登记原控制票 64。新 locals 只有有界控制数值与 caller 原 override 项，不承载 native/payload/source 树。0/63 的失败经原 `_prepare_profile_material` except/finally 重建有限错误并 failed，未访问尚未初始化的 live dict。
3. `input.py:466–470` 仅把 ids list 建立移到原 reserve 后；规则原序、disabled 校验、raw RuleSpec 投影和前像内容均未变。若 reserve 失败，私有 helper frame 由公开 prepare 的有限错误边界丢弃；没有要求 finally 读取未初始化的 ids。
4. `semantic_profile_production.py:54–63` 把四对象 reserve 移到 slots list 建立前。reserve 失败时 `_ProductionCapture` constructor 未返回，外层 `capture` 尚为 None；公开 `execute_admitted_profile_job` 仍清 checked 与其他新局部并移除原异常链，不对半初始化 capture 调 drop。独立故障注入实际核过这一变化。
5. `production.py:98–116` 把同一 `4*MAX_BYTES` hash debit 从 stage7 移到 stage6 的 `before_projection`，没有增加新 hash、parser、reason、compile 或 evaluate，也未改 stage8 Catalog 投影。原 `semantic_execution.py:717–732` 在这一 observer 返回后才投影/编码并调用 input/source/defs 摘要委托，所以新 hash 低限能够先于这些委托失败。此处确认实际执行顺序与清理；本审没有把 `4M` 足够覆盖所有委托的预算命题当作自己的已证结论。

`semantic.py`、`semantic_execution.py` 和 `semantic_profile_restore.py` 与首审固定字节相同。因此真实 defs/Catalog/disabled/原 17L 发生点、同一 parser/reason core、完整 outer7/reasoning15/child11 decoder 与 readonly freeze、所有槽通过后唯一发布、旧 API/wire/error adapter 均未发生新的源码变更。data-only 的 TermInput/SourceRecord/RuleSpec 固定字段、None/空串/language_raw/顺序与 consumer U/D 两层合同也未改变。

## 实际探针与反例

本树自有 `.venv` 执行 `delta-6c1eec4-probe.py.raw`，首执行 exit0、timeout=false、stderr0。完整 argv、cwd、UTC 起止、时长、环境覆盖、139 项 sourcesBefore/After 与完整双流分别保存在 `delta-6c1eec4-run.json`、`.stdout.txt`、`.stderr.txt`，前后 139 项核同。没有覆盖失败日志或用旧版运行充本次证据。

探针首先在新候选原样运行首审保留的 raw 脚本（14 个案例），再执行 5 个 delta 案例；这是 19 个自定义有界案例，不是 pytest 测试数，不能与 root 的 242 专项累加。全部真实计算由原路径产生，wrap 仅观察，注入仅制造有限失败。

| 具体否证尝试                                                           | 本次实际结果                                                                                                                                                                                                                                               |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| objects=0/63 已建计数容器或错误 frame 留物料                           | caps/used/live/peaks/stage_visits/stage_bounds 全 None，state failed，错误 objects/stage0；prepare 公开 frame 七组 material/source/encoded/receipt 局部均 None，无 cause/context。                                                                         |
| objects=64 获得额外隐含容量                                            | live=peaks={scalar:0, objects:64}，caps.objects=64；再 reserve1 被拒绝。                                                                                                                                                                                   |
| stage6 hash 不足仍开始投影摘要，或 native 留到公开 frame               | 实际 reason 恰一次，stage6 摘要委托观察次数 0，错误 hash/stage6，ledger failed；producer 12 个被审局部全 None，无 cause/context。                                                                                                                          |
| capture reserve 前移使半初始化 capture 泄漏或 drop 触发 AttributeError | 在 stage5 四对象 reserve 处受控失败后仍为有限 MaterialFailure，state failed；公开 producer 12 局部全 None，无原 constructor/helper frame 经异常链保留。                                                                                                    |
| delta 使来源或 fullview/晚期清理退化                                   | 原14案例同版通过：core/defs/catalog=1/1/1、L 与 compile Budget.limits 同一对象、raw/compile 顺序保留；U/D raw 往返；完整 7/15/11 signature/rows；producer receipt/record/transfer，以及 fullview freeze/构造/usage/peaks/live/末槽失败均保持首审清理断言。 |

这里的 MemoryError 是受控注入，不是实际 OOM 或 Job cancellation。成功 ledger live0 和保守 retention 的含义未变：操作票终结不等于返回 native/PV/rows 的真实引用释放，更不等于 H/权限。

## 旧测试与运行边界

以固定 Git AST 比较 f677 与新 ref 的四个 writer 测试：既有 test 函数没有删除或改动；input 只增加两个函数（含 0/63 参数化与 64），production 只增加一个 stage6 委托前失败函数。旧 restore/limits 两文件逐字不变。首审对 adoption 原15/21测试无删、仅当时 receipt 真 frame 清理增强的记录继续保留，没有在 delta 中重写或放松输入/assert。

没有重跑完整 pytest/npm check；root 报告的 242 专项及全仓 ruff 不计作本审独立运行。文档与新 JSON 用 existing Prettier 显式 `--ignore-path /dev/null` 检查，实际结果另存 `delta-6c1eec4-format.*`。raw 探针保留原字节，从创建即 `.py.raw`，不引入被全仓 ruff 当作产品源的 active `.py`。

无产品/测试/旧报告/AGENTS/依赖/环境/Goal 修改，无 GUI/native/模型/付费、其他聊天、stage/commit。当前结论只关闭本次来源/schema/受控 Exception 生命周期 delta 复审；预算结论、完整正常 check、指定双方/CI，以及 T01/T03/I06 供应和正式 Job/selected 全链仍按各自实际门完成。
