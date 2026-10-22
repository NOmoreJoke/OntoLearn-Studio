# owner-proposal 独立静态审查

结论：**本份未应用 proposal 静态可接受，未发现须先修改 reader 或退回方案的阻断。** 该判断只认可拟议测试隔离方向与测试意图，不代表 patch 已实施、任何测试已通过或 fullcheck03 已转绿。原 offending name 继续 UNKNOWN，原 wholecheck 1320 pass / 2 fail 继续保留。

输入为供方 `docs/reviews/T03/i05-fullcheck03-static-triage-20261023/owner-proposal.md`，实际 **6513 B / SHA-256 `46084b8ee35d371accb39c54273499a26346a8aa1ef3b8e2977e0911a13ad477`**，本 agent 全文审读。Python 示例只用 ast.parse 做语法结构读取，没有执行示例、导入产品或 pytest。首轮 `independent-static-review-and-unapplied-proposal.md` 原件保持；本报告是对后来具体 owner draft 的追加审查。

## 精确删除与入口

示例遍历 `tuple(sys.modules)`，只匹配八个固定 root 或 `root + '.'` descendant，再通过同一 `monkeypatch.delitem` 删除。匹配不会覆盖 rdflib_extra、xrdflib 等近似名；会覆盖直接/深层 child、值为 None 的 entry 以及 wcwidth native child。提议没有执行任何 target import，也不根据猜测的 rdflib 名称局部特判。

选择 `make_case` 的前端而非只改 `case` fixture 正确：既有测试既通过 case fixture 调用，也在 finalize 私有测试中直接调用 make_case。两入口都必须进入同一隔离路径。八 namespace 的严格范围来自现有固定常量，不复制成容易漂移的第二套名单。

`tuple` 快照和默认 raising 的 delitem 对该受控单线程构造没有静态矛盾：同一个名称只枚举一次；此循环没有实际 target import 或其他异步操作者。方案与 reader 同样以正常字符串模块键为输入，未承诺处理任意攻击性非字符串 sys.modules 键，不为本次全套污染问题增加无关兼容层。

## 逆序恢复与生命周期

已静态核对本树实际 pytest MonkeyPatch 源码：setitem/delitem 保存旧值；undo 逆序处理记录，NOTSET 才表示原键缺失，None 是应恢复的真实旧值。context 以 finally 调 undo。因而同一 MonkeyPatch 中“删旧 namespace → 插入 synthetic”在退出时可先撤 fake，再恢复原键与原对象。这支持 draft 的机制，但尚没有运行测试证明其具体未来实现。

方案明确不 clear 全 sys.modules、不修改旧 package 对象属性、不在 teardown 导入真实包；不在 make_case 返回前退出隔离 context，也不手动 undo 测试共享 monkeypatch。恢复测试用外层 MonkeyPatch 放 sentinel、inner context 做实际构造，退出后立即核 identity，避免等待测试整体结束而无法作恢复断言。这个外内层设计与标准 MonkeyPatch 生命周期一致。

“恢复精确对象”应按 draft 的 keyset + `is` 判定落实；不要降成数量相等、只验证一个 child 或仅相等比较。恢复承诺限于已记录的删除/插入，不扩为 sys.modules 插入顺序、任意未跟踪 import、模块内部状态或多线程导入的全局回滚。当前 draft 不需要实现这些额外能力；如果应用后真实环境暴露新的未跟踪 import，保留证据另行定位，不能据静态接受预判整套必绿。

## 测试意图是否充分

草案已补齐本次所需的关键判定：

- 全八根、直接 child、深层 child、None、近似前缀 sentinel；进入后 inherited descendants 消失、八 fake root 就位，近似名原对象不变，positive 集合仍精确八根。
- 正常退出及**构造中途异常**恢复。首次 fake_module 抛专用异常发生在隔离之后、make_case 返回之前，能覆盖 setup failure；比只在构造成功后抛异常更直接。外层 sentinel 也由外层 fixture 恢复，避免测试自己的污染泄漏到后继测试。
- 同一 clean evidence 先 verify 成功，再注入 unknown child，仍期待精确 MODULE_MISMATCH。这使负例不再可能仅靠既有未知 child 提前触发相同错误码而假绿。
- 保留原 code-recheck 的首次成功 → 修改 loader code → 第二次 LOADER_MISMATCH，不把当前首 verify 的提前失败当作目标负例已覆盖；__file__/origin/loader 等原检查也不在拟删除范围。
- 不依赖 collection/执行顺序，不跳过污染全套环境，直接 make_case 入口同样覆盖。

以上作为**可接受测试计划**是充分且有针对性的；具体测试源码尚未给出，不能提前签它的断言、上下文嵌套和 cleanup 实现。应用时也须保持既有24 supplier/private 和八 distribution 预期、native-unavailable/fake-loader 及错误码负例，不借机弱化 reader。

## 保留的实际失败和后续门

lookup 缺名分支发生在对该 child 的 `_verify_module` 之前，不能通过更改 __file__、spec.origin 或 co_filename 修复。reader 必须继续拒绝已 loaded 而 manifest 未登记的 child；提议只修 synthetic 测试世界与全局 namespace 的闭合性，不证明生产 reader 存在 false rejection。

方案拟写路径只有供方 `packages/engine/tests/test_semantic_build_provenance.py`，需要 root 另行授权应用后形成新测试候选。静态 diff/格式、有界隔离恢复/positive/unknown-child/recheck、集成后的完整检查由实际运行票与资源安排决定；本报告不授予执行。原 fullcheck03、先前98有限测试和未来结果须各自保留身份，不把旧失败重写、不继承旧通过，不扩大到 mapping 受审树、CLI/native、打包或 ABI/loader。

本次只在指定 independent 目录写报告和审计证据；未改 owner-proposal、产品或测试，未运行测试/产品导入/CLI/native，也没有 commit。
