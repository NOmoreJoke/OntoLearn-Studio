# 新 probe 测试源码说明

2026-10-22。唯一测试 writer：`packages/engine/tests/test_semantic_source_package_probe.py`；唯一说明件为本文件。依据固定合同 `ee2b30a2dad35b2d395f9c735aff80371ab41110`（主合同 60953 B／`d2cdc2e6017ad0257f30611d2928a60a116f4dc389cacdfc977c17efe13e2a23`）、本窗 limited closure、source implementation window 及新 AGENTS。base=`5f910b52c69d86a1076b2032e5d3c63e715947f3`，供应22模块仅为固定6891原样副本，不修改其业务逻辑。

本窗只写源码及说明，执行标准库 AST／文本／hash 核验；没有运行产品 import、pytest、npm、probe、CLI、build、DB、native、网络、GUI、heap／OS 检测或依赖安装。因此不存在本测试文件的 passed 数；语法可解析不是测试通过，完整 check／pytest／打包与验收仍后置。

## 测试分层及真实依赖

- harness 边界：三个 exact argv／非法形态、单一 canonical main dispatch；source 与 frozen sealed locator；binary cap+1 读取、descriptor 校验先于 JSON；严格重复键／非有限数／BOM／编码／schema／ID／set 检查；完整 JSONL、单条／总量／terminal reserve、partial write／半行／无进展失败。受控 stream／clock／fault 只验证收集器，不证明业务、进程或物理保护。
- 输入审计：纯输入资产、合法原 `definition.heads` 保留与预计算 firing/material/result 污染拒绝；完整原83／C13／106 operations／54 checks／50 cases／repair／E5 元数据与命名来源；两个 B1 selector 的纯输入尺度、四 ontology、独立 namespace 与 original S1 边界。
- canonical 集成：只使用真实已收 API 与真实 RDFLib 图；literal 独立 golden 验完整 query／SHACL 六字段；真实 scope prepare→同次 result/source→project，再由真实 query／SHACL 消费；真实 material→producer→同次 expectation/allocation→restore→roots，扰动接收 bytes 后保原 expectation，不重签来迎合坏载荷。
- hook／完整 suite：只读 code identity counter，不替换业务返回；真实 reason／Validator、同名其他 code、已有 hook 前置失败及 finally 恢复；完整 header／observation／terminal 与状态、未知失败、未执行、已知拒绝、取消请求／实际终态和 deadline 边界分开。

业务正确性不使用 fake Graph、fake production、mock validator、重新实现 matcher 或 source 输出唯一 expected。测试中的 literal 预期来自有限输入的独立规范判断，完整新 suite 仍需 T05 外部 oracle；源码和包彼此一致也不能自行证明 oracle 匹配。

四件公共资源的实际 bytes/SHA 是 canonical integration 的硬前置条件。`real_resources` fixture 逐项核 `contract_v2.py/schema.json/registry.json/errors.json` 为合同提议6891身份，再在测试函数运行时导入 canonical 产品。缺失或当前5f错版会实际失败，没有 skip、xfail、复制 checker 或假资源让它现在通过；T01未接收前本窗也不运行该 fixture。lock／distribution／全部22源身份仍由实际 probe 的前置检查核实，测试不绕开。

JSON 输入中的转义孤立 surrogate 保留为真实业务负输入，不把它误作原始 UTF-8 不合法；asset canonical 摘要用 `ensure_ascii=True`，业务 payload 的 canonical JSON 仍跟其实际 producer 域。旧规则的原始 heads 属于输入；禁止的是已计算结果，不能用平坦 key 黑名单删规则定义。

只读状态机核对已回报 root：material prepare 默认完成并将 CaptureLedger 转为 transferred；production 内重新 prepare 会再次 begin，必须给新 CaptureLedger 或让 production 自建。复用旧本会被 MATERIAL_LEDGER_REUSED 拒绝。测试中的真实链已使用新 C，不将 transferred 视为 free 或允许再次 begin。

restore-negative 的有限扰动保持同次原 expectation／allocation；不能根据坏 payload／rows 重新签外层 digest。完整 suite 测试要求 mutation 中捕获的 expectation 与原捕获逐字段相同、不重发 allocation，已成功恢复的原 view 保留。该入口可能因外层绑定先拒绝，这不冒充重新验证全部深层防伪；已收深层单测保持原证据域。

静态对接中回报并已从 root 当前文本核对的定点处置：production 改用新 CaptureLedger；restore 否例删除按扰动 bytes 重签摘要；header format 对齐固定合同；stdout 缺 buffer 不再以 AttributeError 穿透；repair 的 eligible=false 仅阻止原 profile 调用，不再误跳过可独立执行的 transfer-repair-before／after shape fragment。测试对这些关键边界有独立断言；这些处置尚无本窗运行结论。

## 不计为本窗已验的边界

受控 JSONL partial write 只能说明逻辑收集器保留实际半行并拒绝当完整记录，不能证明 OS pipe 原子性。受控 monotonic／取消请求只证明安全边界停止新增工作；opaque parser／Validator 的硬超时、signal、reader join、目标实际停止、H 引用／物理票需要后续获准的外部采集和 receipt。不得将 request/stopping 写成实际 cancelled/timed-out。

原 S1 snapshotLoad 会进入 Store／SQLite，保持 HOLD；两个 B1 semantic selector 不运行 Store、不把内存图时间冒充 snapshotLoad。测试也不 import `semantic_samples`、旧 `storage_probe` 或 worker。独立 artifact 不替代 parent `package:dir`，本机／静态资料不替代目标 OS、CI、真人或指定同版双审。

## 冻结状态

测试源码已按 root 完整 suite/main 的实际接口、byte packet `data` 字段、JSONL 记录结构及 input writer 实际 schema 完成定点对接，共 66 个 `test_*` 函数（参数展开数没有执行收集，不能当实际运行例数）。实际纯资产的静态账本为 320 datasets／417 observations，原83／106／54／50范围及71个合法原heads字典已用标准库 JSON只读检查；两档原 assertedText／query SHA 与固定原件一致。真实图数、报告与业务行为仍留待 canonical 集成测试运行。

自有测试源码已用 `ast.parse` 和 `compile(tree, filename, "exec")` 进行语法编译，不执行返回的 code object；重复函数名为0，超过100列为0，未出现 skip／skipif／xfail。静态检查引用的 probe 属性均在实际源码中有声明，另两个是模块标准属性 `__name__`／`__spec__`。本窗未跑 ruff／formatter／pytest／完整 check；它们仍须在后继实际许可、同版资源与环境齐备后执行，首失败原件另存。

测试中的 full run 以模块 fixture 共享一次实际完整采集，避免为多条结构断言重复执行 full suite；两个 B1 selector 另各采集一次，验证无 hook／子集完整性，明确 `freshProcessExternallyVerified=false`、`coldClaim=false`，不把 pytest 内的直接调用冒充 fresh process。controlled fault／clock／stream 没有提供虚假业务返回。

写锁：本文件及测试源码完成最终字节／SHA读取后停止编辑，交 root 冻结组合与独立静态审查。后续实现、资产或接口变化需另作明确 delta；未声明运行通过或合并就绪。不在文件内自引用本文件 hash。
