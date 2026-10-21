# 已授权私有 profile 机制实施记录

正式授权及固定依据见 `docs/reviews/T05/profile-mechanism/implementation-receipt.json`。本阶段在原树内实现7个代码路径、7个测试路径、6个夹具路径；进度与剩余验收以 `docs/reviews/T05/status.md` 为准。

纯 API 接收结构化原 term/source、已声明 catalog 和给定绑定。`compile_rules` 先完成定义/常量/闭合与结论预检；`evaluate_bound_batch` 核给定 when 一致性、全部比较与全部结论，完整输出预算通过后一次返回；`check_firing_group` 只核给定完整组内部一致性。无真实图匹配、授权认证、全局完备证明或结果发布入口。

数值使用标准库整数构造精确有理，并由原十进词法直接量化到 binary32/64；日历独立计算 Gregorian 日序和精确秒分数，保留显式/缺失时区域。source未知保持缺失，原term与值比较分离。已有四个quality导出改lazy加载并保留对象身份；纯模块导入不触旧RDF parser/filter。

冻结保护值不是容量结论。N2计费包括每次输入/输出出现、长字符串比较/排序、basis去重、每个trace引用及受限流式编码；整数乘/除/GCD/移位/幂/转换在分配前计费。单个基础示例的22 trace单位包括firing、两组绑定及其term引用、when及三个term引用、comparison及两个operand引用、两个head及其term引用、proof leaf和basis引用；对象alias不免计费。

夹具预期来自手工采用矩阵、独立精确分数/IEEE位字段和已知日序见证，未用被测输出回填。失败原件、修前/修后输入、原始日志和工具终态保存在本线review目录；代码独审与最终检查按实际候选另记，不沿用中间通过。

最终保护路径补充：已编译对象和解析值使用弱引用的实际对象身份及原始typed digest检查，仅防误用/损坏，不作producer认证。typed编码区分整数/字符串、tuple/list与记录；records只按实际允许class identity识别，不反射输入class元数据。所有直接比较的operator及位置先作exact-type门，位置数字和tuple整数在排序前验位长、按limb收费。hash必须使用本次实际Budget，预扣`max(1, bytes)`，已有编码数据不重复扣semanticInput；数值/日期/lang的扫描和复制另有保守前置费用。

独立审查的首候选不通过、后续真实问题及每次实际修正均保留。facts代表按稳定firing/head顺序选择，完整原term/source仍在每个firing；六数值有序类型对按1/2/3对阈值2核648格，并执行30种算子替换。firing夹具驱动完整输入，对raw/source/位置/双operand/when/proof/heads/facts逐字段核独立预期；不是仅调用同一checker自证。
