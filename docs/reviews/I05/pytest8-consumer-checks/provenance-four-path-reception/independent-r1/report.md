# I05 四产品 provenance 接收独立静态复核 r1

结论：精确接收 Limited Pass，未见新增P1/P2或范围偏移。两提交分别恰4产品与1份原固定合同文档，四文件当前字节等于最终供方，11项保护面保持。完整engine仍NotPass；本轮不执行、不重审四产品算法、不签真实集成或运行通过。

## 根接收与提交链

正式根intake6666B，SHA-256 `77e2b19c826f6438d6a1840b8fe67a460912bf6aa62b57bdc8d33891c88ccb18`全文已读；它明确允许在I05最新完整候选精确接收固定四路径，要求先check再apply，不许回拷旧probe/JSON/lock或用供方旧树代替当前修复树。本审未将其中供方树的旧probe93848B/test73466B误作I05当前预期。

Git独立核验实际链：553a63ce700477e288be895b33269b1d5ecbdc0f → a633ef391344cce60807638ecd942d4e2183c7b4 → 4bb99d99620811766df38d7e29346e3174f82c8c，后者为当前HEAD。a633相对其直接父提交恰4路径；4bb相对a633恰1合同doc，无第五产品。

对固定2fdd→830cdd依照根指定四路径/--binary/--full-index独立生成diff字节，精确等于已保存patch105213B，SHA-256 `7bffd8b6e3e84e074e511b24cb60e766de380b40e3c142631b54d9b5fa2985bf`。本审只在内存计算、未运行git apply。主方实际check/apply、精确stage、cached check、两commit共8份收据全文已读，全exit0，16个原stdout/stderr文件逐件核长度/hash，两个commit stdout也与实际链吻合；未把Git检查当成产品检查。

## 四文件身份

每项均独立核 current = a633 adoption = 4bb HEAD = supplier830cdd1d198bf549b563925a3a47f7f9444710bd = process9c664483686a08aef062a237c710ff4926818c26：

| 路径 | bytes | SHA-256 |
| --- | --- | --- |
| scripts/build-engine.mjs | 8437 | 738f55ef056c3326f812ab9e4ed272a11a332a21a23a78c72fd07b510d31a8ff |
| packages/engine/entrypoint.py | 976 | aaf9f85b59f115ae0646fd31f5305ee588c2bd58a0fbb28d9714c707c9035ef3 |
| packages/engine/src/ontolearn_engine/semantic_build_provenance.py | 46602 | c96f0630b97c02049b9ee2f62f0b44946962b14c0a2ab5c9094eaaa3fa3b7b0c |
| packages/engine/tests/test_semantic_build_provenance.py | 44315 | 0def6d7da0bdc2353c6f524fe8d86d40ab18936b58d58d1cc06bae713f7a3ec8 |

没有重复阅读全文算法或执行供方脚本/测试。供方首审、delta、98项合成测试/F2处置的含义以根正式接收的限定记录为准；本轮未伪称自己重新跑过或重核那些运行。

## 固定合同文档

4bb唯一新增路径为docs/reviews/T03/i05-m08-provenance-20261023/private-contract-v1.json。目标在a633确实不存在，当前/4bb/fixed2fdd精确同36587B，SHA-256 `9d97a6a233b47abc23064a9a8f8330080d62f39b3db981de14a148880e202a04`。

本轮只额外用AST读取reader的CONTRACT_SOURCE单赋值literal，正好等于该原合同路径；不跟入实现或调用prepare。因此补齐是实际builder输入所需的原固定doc，既未改合同，也不是新增第五产品；仍不证明prepare/PyInstaller已经运行。

## 保护面与身份领域

保护清单11项逐件读取字节：除AGENTS外10项current=fixed553a63，包括probe102749B/`2996deca33083754132bf5f4eab8d1e273161b3e5fe722a8ee96856fb5cc0d5b`、test76628B/`d7947f3e90a7226b28aada7f7b6ba0c09393d25295700da2d8ffa65e353b2f68`、两JSON、uv.lock、root/engine配置及package脚本锁。AGENTS本来是未暂存overlay，独立核其仍15147B/`de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，与此前实际保护身份相同；没有假称它等于Git tracked旧版。

整个probe字节未变，足以证明本次未改变CallCounter或consumer frozen拒绝guard，未顺带连接reader、去掉sys.setprofile或修改deadline行为。cached diff为空、unmerged entries为空，即当前无暂存变更/冲突；不把该事实说成整个工作区clean，AGENTS overlay和原未跟踪证据仍应保留。

最新完整源码HEAD现在是4bb，已包含四产品与固定合同；不能继续把23352称为最新全源候选。probe中canonical22的SOURCE_REF/pin领域仍是已审23352，保护字节保持这一点；canonical supplier域与整个Git HEAD域可以不同，不能为了对齐字符串擅自改其guard或把23352冒充全仓新候选。

## 限制

本审仅Git只读、字节/hash、JSON和一个常量AST读取，无产品、prepare/build、formatter、pytest、native、GUI或作者脚本执行；没有修改主树/旧报告。Git接收成功不关闭未解决deadline、frozen consumer接线、实际source/package CLI、root运行前外部binding或整体验收。原NotPass保留，后续必须基于新的完整候选和明确运行授权推进。
