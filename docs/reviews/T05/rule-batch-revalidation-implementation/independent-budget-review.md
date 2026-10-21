# T05 pure 批次复核：独立逐操作预算审查

结论：**固定候选 `16c58c6d0ca56491c7134c4866f9bed5e0f722c5` 的单 child 三池／control 实现与已审 `/2` 合同一致，未发现 P0/P1/P2 预算阻断。** 独立真实 debit 探针通过：紧原限额下 replay 与 production 的六项 usage 完全相同，保存 operand 发行费用逐出现等于原 true 比较费用子集。这个结论限于 pure 源码与给定输入内部一致性，不证明 I05 allocator、恢复器、producer、selected、包或完整父验收。

## 1. 固定依据与实际核验

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-profile-revalidation`；实际受审 HEAD 为 `16c58c6d0ca56491c7134c4866f9bed5e0f722c5`，Git base 为批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 全文读取当前 AGENTS，15852 B／`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；common，17891 B／`e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`。首个合并工具输出有截断，common 已单独全文补读，不以截断内容冒充完整读取。
- 全文读取本目录三份授权：pure 5884 B／`c26d5b90b158ea8e241d48d3129a8e53ffd5720fd3fb76ea9a1e13c502442161`；approved base inputs 5994 B／`d5486d92359fae36363dcf01270394f31e15a92ba16a614a0ba62b2baa621461`；partial import adaptation 2178 B／`d8d9b467534338b59d137fa0127a8f4c5eabb5f9548785cb65950d35b81b1699`。
- 从固定 Git 全文读取新 `rule_revalidation.py`，6288 B／`9e9258cfefdef56f369dad6bb7838afd22478ea6714e4322b2d872d12616200e`；工作区与固定 Git 相同。定点读取预算测试及明确授权的旧 import 测试 delta，不重复另一功能审查 agent 的完整功能范围。
- 21 个 dbb 采用输入已逐项核 `dbb6b36e9259aa79a1fd908b5cfede3064f0c074`、`cf93fe8` 及 manifest 长度／SHA 相等。16c 中其中20项仍逐字相同，唯一 import 测试变化限于授权的首个 partial-composition 测试，第二个 fixture manifest 测试无变化；三新增产品路径也逐项核工作区等于16c。相对5f实际24产品路径，不能简称整个 diff 只有3路径。

本审查没有改产品／测试／夹具、旧21、依赖／锁、其他树或共享路径，没有提交、推送、GUI/native/e2e/HMR；未重跑146专项或全 check。父提供的既有检查是其证据，本报告不冒称自行重跑。

## 2. 入口、限额复制与 control 绑定

`rule_revalidation.py:131–161` 先创建 control 并 debit 入口1，再 `_copy_limits`，随后只 bind 一次 K_i。入口1覆盖合同规定的固定数量 guard、固定字段复制和三池设置，未先扫描用户完整结构。

`_LIMIT_FIELDS` 在模块初始化从固定 ProfileLimits 生成，单次复制只遍历固定字段表；exact ProfileLimits 检查先行，每字段 exact int 拒 bool，非负且不超过旧默认。比较对象均是原生 int，未执行用户映射、迭代、比较或属性协议。新 ProfileLimits 按该固定表构造；三个 Budget 使用这份冻结副本，原外部 limits 不会成为运行中可替换的池引用。

`_Control.bind:47–58` 要求初始 limit=1、used=1；新 K_i 至少含固定常数，绑定后不能按同条件再次绑定。debit 单调增加，不提供 reset／退款或与其他池交换额度；超限前拒绝。这里的固定入口计量是已批准的 debit 约定，不是将每个 Python 指令或分配等价为一单位 CPU 的性能声明。

`_tuple_bound` exact tuple 后只查原生 len。definitions/matches/firings/facts 分别用原 rules/bindings/firings/head_occurrences；facts 没误套 F_i。saved 的 payload/digest/profile 先 exact 类型、常数长度界，再做相等比较；没有额外递归字符串/source 预扫描。数值 limits 合法不证明它来自原 child，模块 docstring 明确将来源与整次 allocator 留给调用方。

## 3. 三池逐操作来源

`_Resources:79–83` 一次创建三个不同 Budget，全部用同一 copied L_i；没有按组创建池、重新默认构造或借额度。

| 操作 | 位置 | 费用归属与上界来源 |
| --- | --- | --- |
| fresh compile 一次 | 163 | replay，原 definitions/Catalog 和原 L_i；原常量／变量／head 校验保留 |
| evaluate 一次 | 166 | 同一 replay；原有序全部 matches，包含 false，原 plan 编码、重复匹配、排序、head/source/proof 费用不变 |
| saved typed 编码一次 | 167 | saved_encoding；合法保存值与原最终输出编码逐字段／逐出现相同，是原成功输出的一段 |
| 保存每 operand 的 check_value | 182–183 | saved_issuance；对应原 true firing 的 compare_values 左右校验，是原执行的输入编码／哈希 work 子集 |

发行校验没有额外 parse；真正恢复／重新发行未混入子集。新模块没有改 `_walk` 的批准记录表、别名计费或 schema，也没有为共享 source、proof、head／operand 去重。完整原 matches 和 bindings 顺序是成本对应前提：如果调用方重新排序或只提供 true groups，函数不能认证“还是原输入”，成功蕴含不适用。

三池各受原完整 L_i 限制。replay 最多 W_i/I_i/O_i；saved_encoding 最多 W_i/O_i、不累计 input；saved_issuance 最多 W_i/I_i、不累计 output。原整数／临时整数、source／term、深度等限额也保留，不仅是三个总字节数。由此得单次 `3W_i+K_i / 2I_i / 2O_i`，不是经验倍数。

新增 Unicode IRI 准入依赖采用的 dbb 同版生产；本代码重用同一 canonical 模块，并未跨用旧1e3生产对象。此次预算证明针对原同版输入操作的对应，不宣称 Unicode 扫描的 CPU 耗时与旧词法政策相同。

## 4. 四条相等边与唯一循环

所有比较经 `_Control.same` 在原生 len 相等前付 `len(left)+len(right)+1`。调用位置分别为：

1. 161：保存 profile 与 PROFILE；
2. 168：fresh.payload 与 canonical_saved；
3. 169：canonical_saved 与 saved.payload；
4. 170：fresh.digest 与 saved.digest。

exact 类型和长度先限住这些对象；fresh 和 canonical 为旧批准函数返回的 bytes／digest。没有遗漏连接边，没有额外复制或哈希比较，也没有把“hash 一样”作为完整校验。

173–183 是唯一显式 group／comparison 遍历：每组先 debit1 再做 exact PreparedFiring 和 comparisons tuple／数量 guard；每 comparison 先 debit1 再 exact ComparisonEvidence 和两次原 check_value。typed encoding 的递归遍历已归 saved_encoding，后面没有第二轮 shape 预扫描。保存值先完整字节相等，再检真实发行身份，因此同字段伪造实例仍不能通过。

令 C=32、H=64、P=35，则最坏 control 费用为：

```text
入口1 + F_i + F_i*C
+ 两次payload比较(4O_i+2)
+ digest比较(2H+1) + profile比较(2P+1)
= 1+F_i+F_i*C+4O_i+2H+2P+4 = K_i
```

实际 L_i.comparisons 更紧时使用更紧 guard，K_i 仍以32作保守上界。每次比较前付费；任何后项失败都不会返回已经通过的前缀。

## 5. definition-only、资源拒绝与整次条件

141–145 在 compile 前拒绝 disabled 带 matches／saved、enabled 非空定义或非空 matches 却没有 saved。合法 definition-only 在163完整 compile 后返回，未 evaluate、未编码虚构 batch、未领取更多额度。enabled 真正空 batch 仍经过 evaluate 和全部比较。原 disabled 若从未有界 compile，不能据“未执行没报错”推出本 compile 成功；pure 源码没有强行保证这件事。

`check_firing_batch:121–128` 保留 resource ProfileFailure；其他失败与意外 Exception 统一 internal。资源拒绝不捕获后重试、不重建 Budget，不返回 fresh、部分结果或修复值。resource 原因／位置仍由批准旧函数的安全字段提供，不序列化原始 lexical/source/path/traceback。

整次求和属于调用条件而非本纯函数提供的 allocator：

```text
whole work <= 3*sum(W_i)+sum(K_i)
whole input <= 2*sum(I_i)
whole output <= 2*sum(O_i)
sum(K_i) = N*(2H+2P+5)+(1+C)*sum(F_i)+4*sum(O_i)
```

只有实际可信账本约束 N≤100、原 child 来源、disabled／失败／重试槽位及 Σ限额，才能采用整次旧上界。函数每次接受一个合法数值分配，不能认证 N 或来源；逐次传默认值不能由一次返回成功升级为整次有界。ΣF_i 未证不能偷换成全局F。外部恢复 R、持有原 matches、完整投影／hash、JSON读回和 T01 生命周期依旧另算，未被三个机制池吸收。

## 6. 自有真实 debit 探针

只执行一个补充预算探针，保留实际 argv、stdout、stderr、exit 和完整执行源。探针手工给定四个有序 matches（值1、2、3、4），两个比较（≥2且≤3）、两个 heads、共享完整 operand/source、重复 proof leaves；明确预期仅2、3产生两个 firing、四个完整 facts。没有图 matcher，没有根据 actual 制作 golden。

先真实生产，再以该次 work/input/output 等 usage 收紧原 limits；使用相同 limits 重新生产并复核。探针仅在内存包裹原比较 check_value、资源创建和保存发行 check_value 来记录前后 debit，不修改产品文件或收费逻辑。原分支16次比较 operand 校验中，保存 true 部分的8次校验与原对应8次费用列表逐项相等。

实际命令为 `uv run --project packages/engine --frozen --no-sync python -B <本目录>/independent-budget-probe.py`，PYTHONDONTWRITEBYTECODE=1；exit0、stderr空。执行后的源原字节保存为 `independent-budget-probe.py.raw`，避免将证据脚本当新增活动产品／lint 源；原执行路径仍完整保存在 binding argv。

| 池／阶段 | work | input bytes | output bytes |
| --- | ---: | ---: | ---: |
| 原 production | 520391 | 119345 | 17834 |
| replay | 520391 | 119345 | 17834 |
| saved_encoding | 49325 | 0 | 17834 |
| saved_issuance | 22456 | 5920 | 0 |

production 与 replay 六项 usage 完全相同：另三项 trace=62、firings=2、head_occurrences=4。saved_issuance 精确等于原 true operand 子集，8次各 work2807/input740；这是具体实例验证，不以实例代替全输入的静态来源证明。

control 实际 used71545、limit71605，差60恰为 `2*(32-2)` 的保守比较数余量；合计三池 work592172，加control为663717，低于 `3*520391+71605=1632778`。合计 input125265≤238690，output35668=2*17834。限额副本不是调用方原对象，三个 Budget 身份各不同，均持同一已复制 L_i。

自有证据固定 SHA：

- 执行源 raw，6511 B／`1dbc0636d6c37b51764ac120d6c449bf98aaeb1a8d24d3ec7ff5aa5ca0036e53`。
- stdout，5084 B／`18c4be34bf3b53f03c5880107f20b331a42aaefa1449007c83373ad0a2ffc4b7`。
- stderr，0 B／`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。
- exit，2 B／`9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`。
- binding，5133 B／`34f6c283f9f7fb68674bac8fc5b178567ef8fd32bd3a92de220bc1fc7c0c4cf7`。

探针没有测整个 I05 allocator、restore/cache/R、跨 child 保存恢复、包内包含、正式 producer、父验收或耗时／内存性能。本报告没有重跑 source40000 见证或父专项／全check，以免重复其既有职责；本轮新增证据仅补真实逐操作 debit 对应。

最终预算审查结论为通过当前 pure 单 child 合同，可交父线汇合功能审查和正常候选验证；正式消费、指定双模型同候选、包／平台、CI／合并及原完整 Goal 的门均未被本报告关闭。
