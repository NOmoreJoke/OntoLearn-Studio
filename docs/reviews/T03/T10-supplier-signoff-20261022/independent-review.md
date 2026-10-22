# T03 → T10 两行供方签认独立完整静态审查

结论：**NEEDS_CHANGE，1项P3文档证据归属错误；未发现其他阻断。** 本结论仅针对下述固定候选的两行供方核对记录，不是两行实际合同已完整、公共schema已获批或可装配实现通过。建议只更正一处反例引用，不增补运行或重新生成历史fixture。

## 固定对象与审查范围

候选仓库：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`；固定提交 `5efed4058a7f740d9d92f6788c90166709f40877`。本轮完整读取候选三文件：signoff.md、input-identities.json、author-checks.json；后两份按文档JSON解释，不执行其中引用的任何代码。

signoff.md 为12771B，SHA256 `717fd0f0a5fce547c6ae22397bd4a814f5488f6463faf4250985bc6b3754956c`。全部11份来源按候选记录的精确repository/ref/path重新读取Git对象，独立核bytes/SHA/gitBlob一致；未改用移动HEAD。语义全文核对S1—S6、T1—T3和T5；T4按限定读取标题及§4“唯一事务与附件可见性”，未从该节之外推定其他合同已覆盖。S5完整展开examples、locatedRejections、finiteParserKindBranches与execution，未重新运行parser或读取其引用的源码/输入二进制。

本轮只读上述固定文档及受保护AGENTS字节身份。未读取三份供方源码、任何caller/费用WIP或其他供方runtime，未调用parser/测试、产品、构建、collector/caller、native或GUI。只在新prefix新增本报告和checks，不提交、不修改候选或冻结来源。

## 唯一发现

### F1 / P3：缺公式缓存反例被误归为S5既有实取fixture

位置：固定候选 `docs/reviews/T03/T10-supplier-signoff-20261022/signoff.md:17`。当前写“最小反例复用S5的EMPTY_SOURCE/重复header/ROW_WIDTH/缺公式缓存”。其中前三类可在S5的5个locatedRejections中定位；“缺公式缓存”没有对应S5拒绝对象。该JSON实际仅有empty-source、duplicate-header、short-row、blank-record、blank-header-field；没有FORMULA_CACHE_MISSING输入、拒绝对象或该项实际执行记录。S5中formula-empty是**成功的明确空字符串缓存**例，不能拿来当缺缓存拒绝例。

S3“缺失、空、稀疏及重复字段”确实说明缺公式缓存触发FORMULA_CACHE_MISSING、无Table。因此该拒绝**语义**有文档依据；问题是把语义描述签成S5已有有限实取反例，超出了精确证据。消费方可能据此认为已有一份完整固定缺缓存反例可直接用于合同fixture，导致本来未供给的材料被标成已覆盖。

最小修正：仅保留S5真实已有的拒绝项；将FORMULA_CACHE_MISSING另外归S3的既有拒绝语义说明，明确它不是S5本次已封存的反例，本轮未补fixture/未执行。不修改S5，不生成替代历史fixture，不跑parser。修正后提供固定最小delta即可窄复审。

## 逐责任行结果

### 1. 可移植来源及实际解析身份

除F1，签认准确区分了私有实际值、设计要求与尚未供给的正式合同：

- selectionId/scope/SourceProof只在进程内按真实对象身份及代次核验；不能变成稳定sourceObjectRef、跨设备身份或写权限。raw SHA/length不认证owner或producer。
- Table精确为source_hash/sheet/ordered fields/ordered rows；Row.number与Cell.text/kind的既有类型、六种成功分支均来自S3。选项与Table分开，未捏造encoding/format/producer/tableDigest字段；kind注解str未被升级成已批公共enum。完整有序值引用S5，不以describe/sample或事实集代替。
- CSV五个encoding词汇、默认utf-8-sig、caller sheet=null与Table.sheet=CSV分开；XLSX encoding=null、inspection sheet=null与显式选表分开。保留实际选项、不静默转码或规范化。新受限profile只能有条件适配，不能删掉既有其他编码能力。
- 真实parser三字段producer/semantics仍未提供或接入；t03-source-parser-v1仅建议。源码/包/库/基础设施hello不构成真实调用认证；不把旧probe扩大为正式worker、目标平台或新版本验收。
- mapping版本、owner/source-row/managed保留有S6依据，但移植typed角色/identity schema及正式export provider仍明确缺项；墓碑/合法undo控制闭包交T01，未猜空集合。
- 无raw保当前及来源、不能直接重跑；正式重关联需新完整options/Table/定义/基线/预演/确认，仍是设计，未冒称已存在API。

### 2. 来源对象准备/传输

该行准确标记为尚不可装配：

- begin/part/seal名称、receiving重复与sealed拒append只是设计方向；未捏造完整字段/枚举/错误码/可调用入口。既有byte副本读取不等持久不可变对象、耐久或GC保护。
- 65536原字节的base64为87384 ASCII；main→coordinator、coordinator→worker两段各自完整UTF-8 envelope计账，begin前同时可容纳，否则拒固定profile。128块覆盖8MiB只限原设计profile；未把8MiB/64KiB作为Q5产品容量或改MAX_FRAME通过。
- C1 raw完整对象一bin成员与传输分块分层；超单raw预算拒绝，无默拆archive raw chunk。T03 raw-source与I06 ZIP InputSeal不同。
- inspection/configure/preview/commit代次与proof失效、取消/迟到、不能复活旧引用的边界由S1/S2/S4支撑；远端取消/phase/restart仍缺，不把本地abort当正式未提交或零Job。
- prepare先于最终plan保护、后绑fingerprint，durable pin/GC claim/引用及receipt接管同唯一权威排序、unknown留pin，直接复用T4§4并结合T3 F14修正；不会让preview前input seal反依赖尚不存在的最终plan。T01仍唯一持久registry/writer，T03/I06未获第二Map/锁/writer授权。

## 下一段计划与恢复规则核对

候选下一段为条件式最小依赖计划：先由T03签固定parser语义/投影，T01 canonical/worker冻结真实typed sourceObject、双段frame、完整结果及持久prepare接点，I06供真实IO/lifecycle绑定；根再给精确路径/依赖票后，仅在T03适配边界消费sealed完整bytes与实际options。这不是本轮施工票，没有越权改sharedwriter/bridge/锁，也没有把F01/F16/Q5 pending扩大为无关技术冻结。

恢复规则已明确使用T3 P3-01较后澄清，未沿用S4“只有未admitted才可新operation”的过窄口径。已有claim先按当前权限及原operation归属只读lookup，不要求旧proof/lease/旧CAS或新人确认；committed返原receipt、admitted续原处理、unknown不换ID。只有writer权威终局未提交且迟到执行/请求已fence，才可能按正式策略新预演确认、新operation。未发现把无receipt、超时、按钮取消或lease失效当成未提交的表述。

## 核验结果与未解决限制

11份固定来源的bytes/SHA/gitBlob核对通过；候选正文及两JSON完整读取通过；受保护AGENTS保持15147B，SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，既有M未纳入任何写入。具体来源精确身份仍以候选input-identities.json逐项为准，独立检查结果另见checks。

待修仅F1；目前不出Pass。修正后的文档即使通过，也仅能证明“已有事实部分覆盖、缺项明确、下一合同/适配边界可审”，不能补齐真实sourceObject、producer/Table-options digest、full-frame profile、prepare/pin实现或目标Win11x64/macOS15arm64 picker/worker/Store/重关联证据。新设计反例未执行；历史6个成功/5个拒绝/6种Cell分支未复跑，不以本报告重认证运行事实。
