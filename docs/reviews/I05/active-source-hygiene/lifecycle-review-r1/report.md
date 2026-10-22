# B1 闭包生命周期窄归因（纯静态，未应用修改）

九条 B023 在已读取的固定实现路径上均未发现跨轮 late binding 实际错误；它们准确指出了循环变量未绑定的语法模式。当前直接 caller 同步调用这些闭包，调用返回或抛异常以后才可能进入下一轮，故不能仅凭告警认定已发生错误，也不能据此保证未来延迟、动态替换场景安全。建议下一候选用逐闭包的 keyword-only default binding 消除这九处隐式跨轮读取；不默认采用 noqa 或全局 ignore。

## 范围与固定输入

- worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-retained-source-review-triage`；观测分支 `fix/I05-retained-source-review-triage`，HEAD `4c84586ce9e7337d57dd4a71f00761d02deb246e`。
- 固定 candidate `401a6844d25b8990606ae82fc85f932cac352d40` 与 process `4c84586ce9e7337d57dd4a71f00761d02deb246e` 的唯一源码 blob 相同：93915 bytes，SHA-256 `43d083eebefbf315509d5fb6276369506dd760006264afd076d754ab3b027230`。
- 先以 stdlib AST 定位，再只输出相关函数必要 body。真实函数名是 `_b1_observation`（L1518–1594），不是任务措辞中的 `_b1_measurement`；该 blob 没有 `_collection` 定义。同步边界是 `_checked_call` 与 `CollectionBoundary.call`。
- 仅阅读该 tree 现行根 AGENTS 和源路径/证据路径的 AGENTS 存在性；没有发现这些子路径上的附加 AGENTS。未读取 retained 外审 prompt/report/native/global、D2fee WIP、其他模块、算术/存储/资源实现或真实结果。
- 诊断来自获准的既有 m06 原流，只认 1 I001 + 9 B023；本任务未重跑 lint。baseline-comparison 是历史输入，不是本次验证。其逐签名相同结论按根提供的既有独立证据接收，本任务不重验 2cf。

## 创建 → 调用 → 返回 → 下一轮

`_dispatch` L1644 直接 `return _b1_observation(...)`。观察函数在 L1525 依次执行 First、Warm，每轮 L1526 创建新的 phases 字典，L1527 创建 timed；timed 仅在本函数内直接调用，没有作为参数/返回值外传。

`timed` L1528 开始计时，L1529 立即调用 `_checked_call(name + "/" + phase, api, call)`。无 collection context 时 `_checked_call` L190 直接 `return function(*args, **kwargs)`；有 context 时 L191 直接进入 `boundary.call(...)`。读取的 `CollectionBoundary.call` 在 L174 同一栈立即调用 function；L170–177 记录尝试和时间；L182 completed 保存的是返回的 value 和 attempt 元数据，未保存 function、args、kwargs；L184 返回 value。构造器的列表为空，check 只执行取消/期限检查；源码路径中没有 await、调度器、任务队列或 callable 回调存储。

调用返回后，timed L1530 才更新本轮 phases，L1532 返回实际 value。之后当前轮按源顺序继续。L1568 把 name、phases、outputs 和序列化元数据加入 passes；L1572 保存第一轮三个 graph 对象。只有这些步骤走完才进入 Warm、重绑循环域中的变量。L1573 还会把 asserted/ontology/combined 重绑回第一轮对象，但此时本函数内已没有待执行闭包。

异常不创建延迟调用：底层抛异常或边界前后 check 抛异常会向上传播，timed 不完成 phases 写入；所读函数没有捕获并恢复到下一轮。返回值可能保存在 completed，并不等于 callable 被保留。未读取 opaque 底层实现，故不保证其返回值类型、内部工作或实际运行状态。

## 九条逐项归因

| m06 原行:列 | 函数/变量                            | 当前创建与消费顺序                                                                                      | 静态判断                                                    |
| ----------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 1529:35     | timed / name                         | 每轮 L1527 创建；各阶段立即从当前 name 组成 stage 字符串，再同步调用；下一轮才重绑 name                 | 未见当前错轮 stage；若保存并晚调旧 timed，会读取后来的 name |
| 1530:13     | timed / phases                       | 同一 timed 同步返回后写本轮 phases；该字典随后保存在 passes；下一轮才创建新字典                         | 未见当前错写；延迟旧 timed 可写后来的 phases                |
| 1540:27     | build / asserted                     | asserted 在 L1533 同步解析返回，L1537 才创建 build；L1552 同步消费并返回 tuple，之后才有下一轮解析/重绑 | 未见当前错图；延迟旧 build 可读重绑后的 asserted            |
| 1549:27     | build / ontology                     | ontology 在 L1535 同步解析返回；同一个 build 在 L1552 同步消费并返回                                    | 未见当前错图；延迟旧 build 可读后来的 ontology              |
| 1554:46     | fixedSelect lambda / combined        | L1552 已得 combined；L1553–1554 创建 lambda 并由 timed/checked_call 同步消费                            | 未见当前错图；延迟调用可读后来的 combined                   |
| 1556:48     | rdfsRules lambda / combined          | 同轮 L1555–1556 创建并同步消费，调用完成后才进入 shapesParse                                            | 未见当前错图；延迟调用可读后来的 combined                   |
| 1560:54     | shacl lambda / asserted              | asserted 来自本轮先前同步调用；L1559–1560 创建并同步消费                                                | 未见当前错图；延迟调用可读后来的 asserted                   |
| 1560:64     | 同一 shacl lambda / shapes           | L1557 shapesParse 同步返回，之后才创建该 lambda；L1559–1560 同步消费                                    | 未见当前错图；延迟调用可读后来的 shapes                     |
| 1567:49     | resultSerialization lambda / outputs | L1561–1564 创建本轮 outputs；L1566–1567 创建并同步消费 lambda，拿到 encoded 后 L1568 才追加 passes      | 未见当前错轮 outputs；延迟调用可读后来的 outputs            |

这里的“未见”限于所读固定函数的控制流及其正常内建实现，不是运行结果，也不是把 B023 宣布成无价值的误报。

## 建议的最窄有意义改动（仅建议）

保持函数 body 与调用位置，使用当前对象的 keyword-only 默认参数：

```python
def timed(phase, api, call, *, name=name, phases=phases):
    # 原 body 保持原顺序
    ...

def build(*, asserted=asserted, ontology=ontology):
    # 原 body 保持原顺序
    ...

# 各自在原 timed(...) 参数位置替换对应 lambda：
lambda *, combined=combined: semantic.query(combined, dataset["queryText"])
lambda *, combined=combined: semantic.reason(combined, _legacy_rules(dataset, modules))
lambda *, asserted=asserted, shapes=shapes: semantic.check_shapes(asserted, shapes)
lambda *, outputs=outputs: canonical_bytes(outputs)
```

这覆盖 2 + 2 + 1 + 1 + 2 + 1 = 9 条诊断，不预绑定与本轮无关的 semantic/dataset/modules，也不移动 parse/build/query/reason/check/encoding 的实际调用。I001 是独立的 import 排序事项，不属于闭包错误归因。

对象身份与生命周期：默认值在每次 def/lambda 创建时求值，保存当时同一对象的强引用；不复制、不深拷贝、不冻结图/字典。timed 捕获本轮 name 字符串和新建 phases 字典；build 捕获本轮已返回的 asserted/ontology；两个查询/规则 lambda 各捕获已得到的 combined；SHACL lambda 捕获已得到的 asserted/shapes；序列化 lambda 捕获刚创建的 outputs。对同一可变对象的后续原地修改仍然可见。若闭包将来被外部保留，默认值会使该轮对象随闭包继续存活，而不是随共享 cell 重绑转向另一轮；实际释放取决于全部引用与异常 traceback 等，不声称引用计数、物理内存或性能变化。

签名边界：timed 保留三个必需位置参数，新增两个可选 keyword-only 参数；build/各 lambda 保持允许零参数且禁止新增位置参数，新增相应可选 keyword-only 参数。签名确实变化，不能称“签名完全不变”。已读内部 caller 以现有三个位置参数调用 timed，以零参数调用 build/lambda，因而现有调用形式保持兼容；未验证外部反射、运行时替换或未来调用者。

计时边界：默认值求值发生在原 def/lambda 创建处，仍在各 timed 的 L1528 start 之前；底层调用仍在 timed 计时内部，并仍由 boundary.call L172–177 包围。阶段顺序、传给底层的当前对象身份和边界前后 check 不变。创建默认值本身可能增加计时外工作，实际耗时数值不能承诺相等；也不能承诺内存/性能收益。若将来改成延迟/异步执行，绑定只能避免跨轮 rebinding，不能自动解决 phases 写入顺序、共享对象原地变更、取消/期限或异步返回语义，仍须另审调用契约。

若决定保留原写法，应把上述同步直调链、只保留返回值以及无 escape 的精确位置作为保留依据，并要求在引入队列/回调保留/替换 boundary/timed/_checked_call 时重新审查；当前必要 lint 门禁仍须由 owner 明确处理，不能靠“目前同步”宣布 lint 通过。相比添加 noqa，局部默认绑定能表达每轮对象归属且不改变现有实际调用形式，建议采用。

## 本次证据与未决限制

本次只运行固定 Python 3.12 的 stdlib bytes/hash/AST 分析与只读 Git；未 import/compile/runpy/执行产品。未运行 B1、canonical、pytest、原产品、环境/安装/构建/打包/网络/DB/native/GUI/Goal/push。没有在冻结 tree 写入文件、AGENTS、index 或 HEAD；没有 apply 产品修改。没有以本次静态归因替代必要 fullcheck 或新候选的独立审查。

原始诊断与历史 baseline JSON 按字节复制留存，未格式化。精确函数证据见 `ast-function-evidence.txt`、`b1-function-evidence.txt`、`boundary-and-caller-evidence.txt`。初次按任务给定的 `_b1_measurement`/`_collection` 名称选择时没有命中，后以诊断所在 AST enclosing function 正确定位 `_b1_observation`，未伪称首次即命中。

`read-receipt.json` 对 git show 只记录实际 stdout 的字节与 SHA，不留整份源码；两份 extract-receipt 的 stdout 字段是 Python 提取器的真实输出，并非所嵌 git show 的全量 stdout。此字段区分详见 `receipt-clarification.json`。这些元数据不表示运行过产品。最终报告、结构化结论和清单的 bytes/SHA 以 `artifact-manifest.json` 为准。
