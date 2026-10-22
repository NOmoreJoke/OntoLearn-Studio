# I05 fullcheck03 两 fail：独立静态复核与未应用 fixture proposal

结论：**支持 packet 的首要归因：T03 synthetic fixture 没有隔离八个 distribution 命名空间的既有 children，与 reader 的完整已加载模块核验不兼容。** 两次实际失败均进入未知 loaded name 拒绝分支，不能归因于 `__file__` 或 `co_filename`。精确 offending name、首先引入它的测试/collection 路径均为 **UNKNOWN**。可评估仅在测试 fixture 入口做可逆的八 namespace 隔离；reader 严格拒绝未知 loaded child 的逻辑必须保留。本报告仅给未应用方案，不宣称修复或复验通过，等待具体 draft 的下一次独立静审。

## 身份与静态证据

输入 packet 的 report 为 6979 B / SHA `7ffc6ef5103ad85900fbd1d346049976e08a550c969d87a2d1b2e5e152864882`，proof 为 38535 B / SHA `7c4dd8ac4f1defa0fde696dc82530a5e4e774634a2af5ed53f8435703a69fd86`。manifest 两成员均逐字节相符。

供方树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-i05-private-provenance` 当前 HEAD 为 `9c664483686a08aef062a237c710ff4926818c26`。独立核对四个产品文件，当前字节都等于产品 `830cdd1d198bf549b563925a3a47f7f9444710bd`：builder 8437 B / `738f55ef…31a8ff`、entrypoint 976 B / `aaf9f85b…035ef3`、reader 46602 B / `c96f0630…3b7b0c`、tests 44315 B / `0def6d7d…7a3ec8`；完整 SHA 已写 `static-audit.stdout.json`。AGENTS 15147 B / de15f6ce…a5c8c4 的 unstaged overlay 保留。未改动四产品、测试或 mapping 受审树，未 commit。

独立读取 packet 引用的原 receipt、stdout、空 stderr 与 JUnit，均匹配 proof 的 bytes/SHA。XML 实际有 1322 testcase、2 failure、0 error/skip，即 1320 pass；两份完整 failure 文本与 proof 逐字一致。proof 中六个相关 source identity 及 11 段引用文本都与对应普通源码原件一致；只读源码/AST，不 import 任何产品、第三方目标或 pytest。

未重新读取 private controller ticket payload，未逐个复查全部 48 个 protected 路径的 before/after；这些仅作为 packet 所引控制/保护记录，不能冒充本 agent 独立完成。source417、native/CLI/frozen/包及性能不在本次证明域。未运行测试、产品导入、CLI、native、安装、check 或构建。

## 失败链：已观察事实与推论

`make_case`（tests:53–206）为每个固定 distribution 只登记一个根 Python 模块 `name/__init__.py`，另有 data；wcwidth 再有 native 记录。`fake_module`（44–50）只对精确根名 setitem；整个 make_case AST 没有 delitem/clear/pop，也没有清理八 prefix 的既存 children。

reader `verify_loaded_modules`（653–670）却从完整 `sys.modules` 快照读取 `name == dist.name` 或 `name.startswith(dist.name + '.')` 的条目。每个非 `wcwidth._wcwidth_c` 名称都必须存在该 dist 的 Python lookup；本 fixture lookup 只有根名。故任何遗留 non-native child 都会进入 668–669 的 `if name not in lookup` 拒绝。原 JUnit 正好记录两次都在 reader:669 抛 `BUILD_PROVENANCE_MODULE_MISMATCH`。

- `test_loaded_module_positive_is_limited_and_has_no_root_approval` 在 tests:372 的 verify 失败，后续 unknown/24模块/8 distribution 断言尚未运行。
- `test_loaded_code_is_rechecked_on_every_post_observer_call` 在 tests:669 的**第一次** verify 失败，尚未改 loader.code，也没有执行后面的第二次 verify。不能说这轮证明或否定了“每次重验代码”。

固定八 prefix 独立由源码 AST 读为 pyparsing、pyshacl、rdflib、owlrl、packaging、prettytable、wcwidth、html5rdf。proof 的 fixedDistributions 摘录从第47行开始，未单独包含开头 pyparsing；该摘录本身不是八项全表。本次已从完整常量独立核足八项，不据这个局部摘录删减范围。

最短静态 collection 链 `test_contract_v2 -> Store -> rdf_snapshot -> rdflib` 与 rdflib 根模块导入 graph/namespace/term 等声明均有原字节依据，证明整套收集可以产生八 namespace descendants。它支持结构性兼容性归因，但没有保存当次循环 name/dist/lookup/sys.modules，不能把 `rdflib.term` 或任意其他示例说成实际第一个 offender，也不能认定究竟 collection 还是先前测试首先导入。wholecheck03 仍为实际 FAIL，不因局部独立单元的历史通过而改判。

## 三个身份域不可混用

1. **名称登记域**：reader:668–669 在 lookup 中查 loaded name。本次失败属于此域，先于对该 child 调 `_verify_module`。
2. **文件/来源域**：`_verify_module` 的 625–627 行实际比较 `module.__file__`、`spec.origin` 与 artifact expected path，并要求在 root 内。改代码对象的 co_filename 不会改变这些模块/spec 属性，也不会补一个缺少的 manifest name。
3. **代码对象域**：`_normalized`（415–422）只递归替换 co_filename，随后 marshal4 指纹比较；这是 loader code 与 source compile 的比较域。不能为该 fixture 失败放宽路径、忽略 child、把代码 normalization 改成通用放行，或改报 `packageCodeBoundToSource`。

## 最小未应用 proposal

唯一建议改动面是供方 `test_semantic_build_provenance.py` 的 fixture/helper 与相应隔离回归；reader、builder、entrypoint、合同、固定输入/版本、错误码及正负预期不变。这里没有生成产品 patch，也没有改测试源码。

在 `make_case(monkeypatch, engine)` **最先**调用一个私有隔离 helper，使用传入的同一个可逆 MonkeyPatch：

```python
# Schematic proposal only; not applied or executed.
roots = tuple(p.FIXED_DISTRIBUTIONS)
for name in tuple(sys.modules):
    if isinstance(name, str) and any(
        name == root or name.startswith(root + ".") for root in roots
    ):
        monkeypatch.delitem(sys.modules, name, raising=False)
# Then construct all existing synthetic modules with the same monkeypatch.
```

精确 root 或 `root + '.'` 边界很重要；不能用裸 startswith(root)，否则会误删类似 rdflib_extra。不要删除全局 sys.modules、clear 所有库、只移走猜测的单个 child，或过滤 reader 的 loaded 列表。包括既有 wcwidth native 名称在内的八 namespace 条目都要隔离，这样 synthetic native-unavailable 前提也有确定边界；没有导入或执行真实 extension。

现有 pytest monkeypatch fixture会在整个测试生命周期后 undo，且其 setitem/delitem 以逆序恢复旧值（包括 None）；本 agent 只静态核了供方自身 `_pytest/monkeypatch.py` 的 context/finally/undo 源码，身份与片段保存在 `monkeypatch-source-evidence.json`。同一 MonkeyPatch 的先删旧 root/children、后设 fake roots，在 teardown 逆序撤 fake、再恢复旧对象，符合最小改动方向。`make_case` 的直接调用方 finalize 单元也应经过该入口，而非只改 `case` fixture 包装层。

不要在 make_case 返回前退出一个局部 context，否则 case 用到时隔离已撤销；也不要在 fixture 中手动调用共享 monkeypatch.undo()，那会同时撤销调用方其他 patch。若使用独立 context，应把整个 case 使用生命周期包在 yield/finally 内，并处理直接调用 make_case 的单元。具体 draft 应选择一种明确生命周期，避免两套互相叠加的清理。

恢复承诺只限八 namespace 的 key 存在性和**原对象 identity**及通过该 MonkeyPatch 跟踪的更改；不宣称恢复任意模块内部属性、sys.modules 插入顺序、其他线程/任意 import side effect。若使用期间可能新增未由该 MonkeyPatch 跟踪的 child，必须明确检测/清理或禁止该路径；不能仅凭 delitem/undo 声称所有任意新增状态都会消失。真实 namespace 被短时替换也可能与 pytest plugin 动态导入交错，静态方案不能预先保证整套兼容性，后续获准的整套复验仍必要。

## draft 必须覆盖的正例、负例和恢复边界

以下是待审 draft/后续获准验证的验收要求，本次未执行：

- 对**全部八 prefix**预置根、直接 child、嵌套 child 的 sentinel，不 import 真实 target；确认 make_case 入口清除旧条目，synthetic baseline verify 的 loadedDistributionModules 仍精确为八根，private/supplier 仍24。
- 纳入原值为 None 的条目、wcwidth._wcwidth_c sentinel、名字相近但不属 root-dot 范围的 unrelated sentinel；前两类可逆隔离，后一类始终保留 identity。
- 正常退出和主动异常退出各验证 prefix keyset 与原对象 identity 精确恢复；还需覆盖 fixture 构造中途失败的 cleanup。不可只断言某个 child 不在，或只数数量。
- 保留原 unknown-child negative，并在同一 case 中**先 baseline verify 成功**，再注入 `pyshacl.unrecorded` 后期待相同 MODULE_MISMATCH，避免 inherited 污染提前命中相同错误码造成假阳性。注入项需走可逆 patch。
- 保留并实际走完既有 code-recheck 的首次成功→变更代码→LOADER_MISMATCH 链，及 __file__/origin/module identity、fake/absent native 与 immutable evidence 原负例；不调整这些语义预期来凑绿。
- 如果对同一个 helper 的隔离/恢复声称依赖 pytest 自动 teardown，要用独立 context 验证恢复而不直接 undo 测试共享 patch；即使 assert/构造抛错，原 namespace 也要回来。新增测试只用合成对象和现有 reader 私有接口，不扩成 target imports、real semantic/native 或任意 CLI。

以上边界在原 packet 的方向性一句“可逆隔离”中尚未逐条明确，不能把它当已完备 patch；属于 draft 的最小验收补全，而非要求放宽生产 reader。根后续给出具体 draft 后，需独立检查精确字节/差异、生命周期及这些恢复/负例是否真正成立，再由 root 安排运行票。本静审不给 future run、wholecheck 通过、native 或产品批准。
