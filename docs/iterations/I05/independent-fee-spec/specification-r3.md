# I05 逐 occurrence 收费规范 R3：完整失败入口（提案）

R3 是收费模型的新提案版本 `i05-reference-fee-program/3-proposal`，回应正式 R2 Fail 的 F1/F2。它继承 [R2 规范](specification-r2.md) 的 binder、primitive、typed 编码、排序/完整 key/hash、五 operation 全动作目录、allocator 余数和既有 cap；以下条款替换 R2 的完整入口错误出口、静态 compile、最终化与 receipt。R2 原件及其独审 Fail 均保持。新候选是否关闭发现由独立 delta 审查判断。

## 1. 不变的边界和完整载体

固定 82+32 的原输入、声明、独立数学 expected 和窗口/amendment 许可不变。只运行本目录 stdlib 纯数据/数学/收费解释器；局部图和绑定只用于枚举费用，不输出业务 expected、不发行产品对象、不向 T05 提供 oracle。`per-id-r3.json` 为全部 114 项逐 ID 可判定表，`charge-reference-v3/all114-fee-programs-r3.json` 给每项完整输入绑定、数学值、cap、分析金额、实执行前缀、receipt 与重建配方。任一 ID 均无 caller 后供的收费金额。

`amount` 是新提案程序在完整数学分析中的需求，遇到真实语义错误只到该错误为止；`paidPrefix` 是严格数学执行器实际接纳的向量。二者都不是产品实付 usage。`predictedAllocation` 与原数学 expected 保原值，现行 exact、真实同次 17L/issuer/usage、现行编码和许可发点权威分别 pending；提案金额非空不消除这些缺口。未构造的 native/payload/rows 字节为明确未构造的 `None`，绝不补 0。

完整 baseline 双 tape 保存在 `baseline-prefix-r3.json`。六个原独审纯输入到完整失败 invoice 的双 tape 保存在 `complete-failure-programs-r3.json`。其余 113 项可由逐 ID 配方的固定输入指针和 `--events ID` 重建完整事件；没有只支持正向分支的第二解释器。

每个term.source和definition.source occurrence在C0完整验证/编码扫描；合成SourceRecord的text摘要同样逐occurrence收费。不得按Python id省这项票；ENTRY的完整term/source INPUT、raw scan和完整key/fingerprint仍各自逐出现收取。alias只影响已明确的持有关系，不提供省复核/扫描/输入费许可。本条是最小新提案的确定定义，不是已证现行收费。共享2对象与JSON6对象图的差异及最终等额反例见手算；没有把未知cache hit价格补0。

## 2. 静态生命周期证明先于执行

整个完整入口先从纯输入按 R2 固定动作目录生成收费分析程序。此阶段枚举真实数学检查和收费动作，发生真实 `parse_math`、`compare_math`、compile、receiver 等错误时捕获实际出口，附加有限错误枚举动作并停止该语义路径，不伪造后续对象或成功尾段。局部 primitive 仍可向独立数学调用者抛出本来的错误；公开完整入口统一封装其失败 invoice。

在创建严格执行账本前，对该完整收费程序做全静态证明：所有 HOLD 的名称全程唯一；objects/scalar 非负整数；每个 RELEASE 对应此前活引用；control 只允许 terminal cleanup；累计 data handle 数 h 小于 2^32，累计 objects slots s 小于 2^64，释放不返累计名额。不把 unexecuted 尾项的释放计成执行余额，不从最后 live 倒推 h/s。R1 已通过独审的小 Ledger 的 h0/s0、差 1、最后 handle、释放后不回流规则保持，本次没有修改或重跑无关小模型。

然后构建 `bootstrap control64 → H01 → 全部原收费动作`。H01 的整个 work/scan/hash/receipt 持有向量与普通动作一样原子预付；它包含该程序所有累计清理票，故即使较早拒绝，未执行尾项不产生新清理债。workspace 的最终最大 arena 从该静态程序在首次使用前预留，不能等资源消耗后再借 RELEASE 获取余额。实际执行新建账本只发生在上述证明之后。

生成器内部错误（无效生成生命周期、固定宽度证明失败）是模型自检故障，不能冒充业务 RESOURCE_LIMIT 或完整方案成功；自检命令非零退出必须保留。支持域为授权 plain JSON 输入及固定数学 profile；不声称任意 Python 对象/循环引用可作为业务输入。

## 3. 严格执行与首错

每动作先计算该钱包的全向量尝试值：累计九域 `used + charges`、同时活着的 objects/scalar `live + hold`。按固定顺序 work、input_bytes、output_bytes、trace_items、firings、head_occurrences、bindings、scan_copy、hash_bytes、objects、scalar 找最早超 cap 的域；任何域不足则该动作所有收费和持有均不发生，记录 `debited=false` 的拒绝动作。先 HOLD 再检测或只检测 work 均不合法。

接纳动作后才允许执行其对应真实数学检查。实际语义检查失败记录 `INVALID_RULE`、`INVALID_LITERAL_LEXICAL`、`UNSUPPORTED_LITERAL_DATATYPE`、`UNSUPPORTED_NONFINITE_LITERAL`、`RULE_COMPARISON_TYPE_MISMATCH`；已规定 primitive/结构上界触发 `RESOURCE_LIMIT`，内部独立数学一致性问题另记 `INTERNAL_MATHEMATICAL_CHECK`。错误内容仅有限 reason/phase，不把任意 exception 字符串、源文本或 traceback 塞入 receipt。真实异常分类表是 reference 的规范组成，不从产品错误消息学习。

若数学分析在后段发现词法错误，但严格执行已在前段整向量拒绝，`firstError` 仍为该前段 resource；`semanticAnalysis.reachedByExecution=false`，它只说明分析观察到了该错误。严格执行 tape 不包含该语义错误动作。不能将分析尾段称为已执行，不能用抑制异常返回成功，也不能把手填小状态机的 error 动作代替真实完整入口。

首错后只做 H01 已预付的 terminal 清理：释放所有活 data arena、输入、临时 producer/project/wire/receiver/cache 引用、receipt 与 control；终态 failed/live0/无 retained handles，禁止发布已成功部分。累计账不退、不加票、不 reopen。成功路径遵循五 operation 原 retention：profile 留 native+receipt；restore/DAG 留 restored native+roots 返回 buffer（如调用）+receipt；negative 只留其有限拒绝的 receipt。控制对象一直表示仍活的 caps/used/live/peaks/stages，普通 alias/RELEASE 不能提前释放它。

## 4. 每条定义的完整静态 compile

所有 enabled、disabled、零匹配定义均先完整 compile，然后才进入图闭包、匹配或 firing。已知常量和依赖 binding 的检查分开：变量只延迟依赖其值的部分。

每个 when/head triple 收 3 work 的位置检查并要求 arity3；predicate 必须固定 IRI，subject 为固定 IRI 或合法闭合变量，object 为 IRI/literal 或闭合变量。when predicate 为 Variable 是结构错误，disabled 也不能跳过。变量 grammar、闭包与已有结构 cap 原样执行。

每个 head 在位置检查之后，对 Catalog 每个原声明完整 occurrence 收 `len(声明 UTF8)+len(predicate UTF8)` 的 scan/work，随后 1 work 检查受控引用。常量 predicate 必须为 rdf:type 或已声明 object/data property；rdf:type 的已知常量 object 必须为已声明 class；object property 的已知 object 必须 IRI；data property 的已知 object 必须 literal。即使 subject 或 object 的另一槽是变量，上述已知检查仍必做。变量 object 的 class/kind 校验只延后至实际 binding；不从 heads 给 Catalog 补许可，不扩整数政策或 cap。

baseline 一条定义新增 4×3 when + 3 head + Catalog 完整扫描 785 + 受控引用 1 = 801 work、785 scan、16 动作。其它定义据其自身全部 when/head/Catalog 计算，非统一加 801；dummy 没有凭空的 head 检查。

## 5. IFR3 receipt 与持有

IFR3 用 R2 固定大端 LP/u32/u64 布局，magic/version 改为 `IFR3`/3；末尾 status 后新增 reason u16、首错 plan ordinal u64。status0=success、1=semantic failure、2=resource failure、3=internal mathematical failure。reason 按上节有限枚举，NONE=0；成功 ordinal0。receipt 内 11 域写严格执行已付九域和严格执行两 live 峰，绝不写分析需求。17L 是新提案分配预测；它不能充当 OriginalAllocation capture。

末尾 programHash 为 `SHA256(canonical executionEvents)`，与另存的 `programSha256`（分析 tape）严格分开。footer 为 `SHA256(b'I05-FEE-RECEIPT/3\0' + body + 32个零字节)`。payload native/view 的 proposal codec 与数学内容格式继续使用原 `/2`：这次不改其字节编码或业务语义；只有收费程序和 receipt 版本升级，避免无因全量涨价。

令 W 为已开户钱包数、N 为已预测分配 child 数（ENTRY 首错时 child 可能已有预测但 M 尚未开户），R 为该 receipt 精确字节数：F=14+12W+20N，H01 work=F+3h+s+4R、scan=4R、hash=18+R；receipt 从 H01 起并持 objects F+1、scalar2R+32。成功只保原 operation 所有返回引用；失败将 receipt 逻辑引用也清零，返回的有限数学证据文件本身不声称产品发行或免费保存。

若 binder 在原分池所需 Q/D 尚未构造前失败，不把未知 Q/D 当 0。使用原非负合同的固定下界 A≥8MiB+16MiB、N≥1 对应 C0 slice；先 control64、完整 invalid-entry ASCII 输入 scan、真实 binder 错误、H01 和终态清理。注明 binding-not-completed/源字段未构造，不伪造 dummy child 或 source permission。固定 114 均不用该 fallback；它用于完整入口早期无效输入的可复核失败。

## 6. 验证及实施 delta

新 source 位于 `charge-reference-v3/`，v2/R1 所有文件冻结。13 个原 typed 数学测试的字面 expected 不改，增加 10 个完整入口方法，包括六个 R2 原反例、已知 class/property 常量+变量、原始 N3 binder 错误、Unicode、晚 receiver、非有限/越界/非法日期/未知 datatype。独立 `audit_execution_r3.py` 不 import reference 或 Ledger，重建全 prefix/持有/峰/原子拒绝，独立第二 encoder 与 IFR3 decoder/hash/17L 预测交叉，字面手算另见 [R3 小账](hand-examples-r3.md)。114+6 双 seed 同时核分析/执行 hash、金额、paidPrefix、首错和 receipt。

I05 必要产品实施 delta 仍待独立后续：将各入口真实错误接入有限 finalization、把整条生命周期/receipt 票证明接到同次真实预算、按完整静态 compile 检查已知常量、原子预付整向量并留真实 usage/capture/issuer、失败清理无成功部分。五 operation 的 R2 动作目录和源字段绑定仍须独立实施，不能只加一个通用 event calculator。T05 受审候选不修改；后继纯规范 carrier 可以采纳本提案，但既有 6891 当前代码遵守与否仍未证明。
