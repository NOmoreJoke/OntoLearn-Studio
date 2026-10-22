# I05 CallCounter 选择性监控纯设计

结论：两个现有同步函数的真实调用计数可以设计为 `PY_START` + code identity + 当前线程过滤；但不能把 `get_tool(id) is None` 当作干净监控槽的证明。Python 3.12 的公开 API 无只读 callback getter，也不枚举所有 code-local 配置。在要求“绝不短暂改动残留的外来 callback”的严格解释下，本方案尚不具备一般性实施就绪证明。下文分开可证的计数设计与这个准入缺口，不以实验或放宽边界补结论。

本次只用官方文档、固定 Git 源码和自有环境中的文件字节/AST；未 import 产品或 pySHACL，未调用任何 monitoring API、创建线程、运行 pytest、collector、benchmark 或 OS 研究。原417项、120秒、64MiB和业务实现不变，不量化任何收益。

## 固定前像与目标

前像 `553a63ce700477e288be895b33269b1d5ecbdc0f`：probe102749B / `2996deca33083754132bf5f4eab8d1e273161b3e5fe722a8ee96856fb5cc0d5b`；test76628B / `d7947f3e90a7226b28aada7f7b6ba0c09393d25295700da2d8ffa65e353b2f68`。没有读取或采用后继 T03 四产品。

现有 CallCounter L710–739 捕获 `semantic.reason.__code__` 与 `Validator.run.__code__`；仅对当前线程 profile 的 `call` 事件作两个独立 `if`，所以同一 code 对象占两个角色时，两计数都加一。进入前拒绝非空 `sys.getprofile()`，退出时恢复。计数不是函数名称匹配，也不是按照预期次数填结果。

固定 `semantic.py` 的 reason L1247–1258 是无 decorator、无 yield 的同步 def；实际文件66258B / `d6c5f5c38aec310de726f73568e1086bf4de95117cbdf664ae1384fcd6808392`。自有 `.venv` 的 `pyshacl/validator.py` 为16430B / `18840545f2146c0f5b9eea60b665099c992f9d56f9f0a060df07c07889a6a129`，run L175–324 同样是无 decorator、无 yield 的同步 def。直接 AST 检查支持本版本只需入口事件，不把此结论扩为 generator/coroutine 的一般计数。

## 官方 3.12 契约

| 事实 | 对本设计的约束 |
| --- | --- |
| PY_START 在 Python 函数开始时交付，参数为 code 和 offset；PY_RESUME/PY_THROW另有意义 | 对已核两个普通同步目标使用 PY_START；未来目标变为生成器/协程必须重新设计，不能静默少计。 |
| 可对指定 code 设置 local events；local events与global相加 | 只新增两个目标的PY_START，不启用全局事件，不声称它能屏蔽既有global设置。 |
| monitoring按interpreter，setprofile按thread | callback必须过滤本次enter的owner thread；不能把别线程同code调用纳入旧计数。 |
| use_tool_id在已占用时ValueError；合法用户ID为0–5，PROFILER_ID=2 | 固定尝试2，冲突就拒绝，不扫描其他ID绕开占用，不抢占debugger/coverage。 |
| 3.12 free_tool_id只释放名字，不取消callbacks/global/local事件 | 清理必须先停事件、取消自己的callback，最后释放；不能套用3.14 clear/free行为。 |
| register_callback是交换，返回旧callback；注册/取消会发audit事件 | 没有只读callback查询。不能吞掉audit异常当成功；它也形成下述准入缺口。 |
| DISABLE会停止特定位置后续事件；restart_events作用于所有tools | callback始终返回None，不用DISABLE，也不调用全局restart_events。 |

以上依据：[3.12 monitoring文档](https://docs.python.org/3.12/library/sys.monitoring.html)、[与实际解释器版本一致的v3.12.12文档源码](https://github.com/python/cpython/blob/v3.12.12/Doc/library/sys.monitoring.rst)、[PEP669的per-interpreter规定](https://peps.python.org/pep-0669/#specification)、[setprofile文档](https://docs.python.org/3.12/library/sys.html#sys.setprofile)。网页当前3.12分支显示3.12.15；涉及精确清理/副作用的结论另以v3.12.12源码核对，不拿搜索结果中的3.14行为代替。

## 可保持的计数语义

callback的逻辑仅为：若未active或当前thread不等于enter时的owner则返回None；随后分别比较 `code is reason_code` 和 `code is validator_code`，各自加一并返回None。alias、不同函数对象共享同code、同code双角色、递归与嵌套的真实入口仍按code计；不同code即使同名也不计。不替换被测callable，不根据case已知预期0停监控。

owner使用本次enter时 `_thread.get_ident()` 的cookie。它可被线程退出后的新线程复用，因此只在同一存活线程执行的规范with生命周期内使用，并要求exit同owner；不能把此cookie当跨线程历史身份或跨进程身份。[官方_thread文档](https://docs.python.org/3.12/library/_thread.html#_thread.get_ident)

两个同步目标正常返回和直接抛异常都会先开始执行，故都计入口一次；在到达目标前被policy拒绝则计0。无关函数、C函数和其他线程的目标调用不加计数。对象在多次规范with中复用时保留原累计counts；每次enter重新捕获owner，不在失败entry中重置外层状态。

这只论证固定目标的入口计数领域。全局profile与monitoring会给进程不同的观测状态和调度开销，不能承诺所有反射观察或耗时相同。既有source/PYZ code指纹仍按实际loader和既定compile/marshal域校验，不因事件设置而反推source等价；probe实现改变后必须冻结新完整source。v3.12.12的公开co_code由去专门化后的字节产生，仍应在后续有限单元核对事件启用前/中/后的既定指纹，不仅凭这个源码事实预签所有loader。[codeobject.c](https://github.com/python/cpython/blob/v3.12.12/Objects/codeobject.c#L1433-L1469)

## 生命周期方案与必须解决的准入缺口

拟议仍保留CallCounter的构造、with和counts接口；新增内部owner、acquired、attempted_codes、callback_registered等状态，不新增调用方批准位或环境gate。

1. enter先检查self未active/未acquired，再检查原sys.getprofile必须None。先拒绝self重入，避免失败entry改写外层恢复状态。目标必须仍是已验证的两个真实普通同步code对象。
2. `get_tool(2)`非None则以私有harness拒绝退出，完全不改外来tool。调用`use_tool_id(2, owner-specific-name)`时仍捕获竞争产生的ValueError；只有成功后才标acquired。没有“抢一个别的空槽”的fallback。
3. 检查本槽global mask为0、两个去重目标的local mask为0；不为清出空间覆盖非零前像。拒绝路径只释放自己刚占的名字，保留原mask。对未占到的槽绝不cleanup/free。
4. **这里存在准入缺口。** 即使上面都为0、名字空闲，先前工具仍可能在其他code留local mask，或留一个PY_START callback。3.12.12 use/free只改名字，`get_local_events`只能查询给定code，`register_callback`只能通过交换拿到旧callback，没有只读getter。不得声称这些检查证明了空白slot。
5. 受限合作式实现可交换注册callback；若返回旧callback，立即恢复并拒绝，且把active保持false。但是这已短暂替换过旧callback，audit调用也可能执行其他代码，故**不能满足严格“任何外来残留callback从未被改变”的承诺**。未知其他code残留local events还可能开始调用新callback，即使被identity过滤而不误计，也不能声称全解释器只有两个code触发callback。当前报告不把这种交换方案签作无条件可实施。
6. 只有准入策略被明确解决后，才进入后续状态机：先注册callback；对每个去重目标在尝试set_local_events前登记它，再设置PY_START；全部成功才active。不能只登记成功项，因为v3.12.12设置local mask以后再做instrumentation，后段失败时mask可能已经变更。[instrumentation.c](https://github.com/python/cpython/blob/v3.12.12/Python/instrumentation.c#L1699-L1853)
7. 退出或entry失败回滚：先active=false；在仍确属本实例的tool上，对所有尝试过的code关闭自己的local事件；确认没有自己启用的global事件；取消本实例callback；再释放tool名字。每个步骤即使前一步异常也尝试其余安全清理，且只对自己成功取得的资源操作。不能只free名字。
8. 若清理失败，不能返回成功观察或把它当业务拒绝。应保留私有harness失败并隔离未清理的工具资源，不将仍有callback/mask的槽释放给后继实例；不得在失败后继续产出“可靠0”。原业务异常与清理故障的优先级必须明确为不能掩盖计数器完整性失败，不能吞异常凑完整采集。

严格域下的结论是先停在第4步的设计问题：当前公开接口不足以只读证明任意复用槽完全干净。它不是本机已发现foreign tool的断言，也不是说计数逻辑本身不可实现。若主方接受合作式已释放slot的精确定义，交换/恢复可以作为另外明确约束的方案审查；若必须保证绝不短暂触碰残留callback，则不能直接实现这一路线。不得新增一个由caller自报true的“slot洁净证明”绕过问题。

## 后续必要验证计划（本轮未执行）

| 验证 | 必须断言 |
| --- | --- |
| 保留现有真实target测试 | 同名不同code为0；reason alias为1；真实Validator入口为1；policy在入口前拒绝为0；sys.getprofile保持原对象。 |
| 直接异常、递归、嵌套目标调用 | 每次真实入口均计；异常不吞；同一code两个角色时两者都加；调用后资源恢复。 |
| foreign profile、occupied tool、自身重入 | entry拒绝且外来hook/name/callback/masks不被接管；外层counts/生命周期不被内层失败破坏。 |
| owner线程与其他线程 | owner存活期间其他线程调用同code不增加counts；owner嵌套调用仍计。这里是未来功能验证，不是当前创建线程的授权或执行记录。 |
| stale配置 | 非零global/目标local先拒绝；旧callback交换路径若被采用必须原样恢复；未知code-local残留及先前DISABLE位置必须有明确接受/拒绝规则，不用全局restart。 |
| 局部初始化故障 | 在reserve、callback注册、第一个/第二个local设置各处失败，回滚所有可能已变状态；不能把slot2占用留给下一case。 |
| 清理故障与foreign替换 | 不free不属于自己的槽；清理失败不能报告成功/可靠0；明确body错误与cleanup错误处理。mock只能证明状态机，不冒充真实监控。 |
| 实际Python3.12与代码身份 | 有限真实监控单元比较两个target的code身份与既定指纹，检查local/global/callback/名字复原；测试不能依赖3.14 clear_tool_id。 |

完成方案独立审查和边界决议后，主方才安排必要源码实施与有限单元；通过后再按实际改动做一次必要原full-v1验证。417项与固定预算不变，不能从PEP的低开销目标或这份静态设计推出本项目会在120秒内完成。

本报告不替代整体指定双审、实际包内loader/native、source/package parity、OS/whole-H/RSS或发布验收。
