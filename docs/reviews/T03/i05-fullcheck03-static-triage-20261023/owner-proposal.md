# I05 fullcheck03：供方静态判断与未应用方案

结论：两项实际失败落在 `verify_loaded_modules` 第669行的已加载名称缺失分支。供方 synthetic fixture 只替换八个 distribution 根名，却保留进入测试前已存在的同前缀子模块，与 root-only manifest 不闭合。应修复 fixture 的进出隔离，保留 reader 对未知已加载模块的拒绝。具体首先触发的模块名仍为 UNKNOWN。

## 固定证据与边界

- 本方 HEAD `9c664483686a08aef062a237c710ff4926818c26`，产品候选 `830cdd1d198bf549b563925a3a47f7f9444710bd`。未修改四个冻结产品文件，未运行测试或导入产品。
- I05 实际集成 source `9d86ef183b2bfc4d2ac6f1583ceb9a5b29cdf876`，原全量结果1320 pass、2 fail；先前本方98项独立通过不替代这次全链失败。
- 精确交接目录 `/Users/kyle/Documents/工作/知爻/本体/outputs/20261023_i05_fullcheck03_static_triage/`。实际核对 `report.md` 6979B / `7ffc6ef5103ad85900fbd1d346049976e08a550c969d87a2d1b2e5e152864882`；`proof.json` 38535B / `7c4dd8ac4f1defa0fde696dc82530a5e4e774634a2af5ed53f8435703a69fd86`；`manifest.json` 627B / `36936a233d39bdacc7efc30d321fff2c5df27fb5f85cdcefa2d12ac2e08156d5`。
- 本报告只提出未应用改动与后续验证方案。未重跑、未修改产品/测试/锁文件；不触碰 mapping 两棵 `c1e44` 冻结受审树。

## 已确定与未确定

`make_case` 第43–50行的 `fake_module` 逐项执行 `monkeypatch.setitem(sys.modules, name, module)`；第92–140行每个 distribution 的 manifest 仅登记根 Python 模块及 data/native 文件。已有 child 不被删除。reader 第658–669行却遍历完整 `sys.modules` 中等于 distribution 名或以“名称 + 点”开头的项，逐项要求其 Python 名已登记。原 trace 确认失败位于 lookup 缺名分支。

这发生在该 child 的 `_verify_module` 调用之前，因此不是本次该 child 的 `__file__`、`spec.origin` 或 `co_filename` 比较失败。`co_filename` 的递归规范化是代码指纹规则，与名称查表缺失不同；不能通过改指纹或路径校验解决此 fixture 问题。

全套 collection 的 `test_contract_v2 → storage → rdf_snapshot → rdflib` 模块级 import 链提供具体静态可达来源；不能据此认定首次 offender 为某个 `rdflib.*` 名称。原 trace 没有记录循环局部变量，也没有对应运行时 `sys.modules` 快照，名称及首次引入时刻保持 UNKNOWN。

第二项 `test_loaded_code_is_rechecked_on_every_post_observer_call` 在第一次 verify 即失败，修改 loader 与第二次核验断言没有执行。原有 unknown-child negative 使用相同错误码；全套中它通过不能证明命中了主动注入的 child，需先建立 clean positive 再注入以提高归因强度。

## 最小未应用改动

唯一拟改产品路径为供方测试文件 `packages/engine/tests/test_semantic_build_provenance.py`，不改 reader、build helper、entrypoint、契约、锁文件或 I05 文件。

在 `make_case` 最前端、构造任何 fake 模块之前，用传入的同一个 `monkeypatch` 对八个固定根及点分隔后代执行删除。示意代码尚未应用：

```python
for name in tuple(sys.modules):
    if any(
        name == prefix or name.startswith(prefix + ".")
        for prefix in p.FIXED_DISTRIBUTIONS
    ):
        monkeypatch.delitem(sys.modules, name)
```

选择 `make_case` 而非仅 `case` fixture，是因为第594行另有直接调用；两种入口均需一致隔离。`tuple(sys.modules)` 只冻结当前名称，避免遍历时删除改变尺寸。只匹配精确根和“根 + 点”，不匹配 `rdflib_extra`、`xrdflib` 等近似名。包括 `None` 值、native child 与任意深度 descendant，不能只删除猜测的某一个实际库子模块。

所有删除及后续 fake 插入由同一 MonkeyPatch 记录，按逆序 undo 恢复测试前的精确对象（包括值为 None 的条目）；不得 `sys.modules.clear()`，不得自行在 teardown 导入真实包，不改 package 对象上的属性。pytest 的 `monkeypatch` fixture 负责异常路径清理。显式隔离恢复测试采用 `pytest.MonkeyPatch.context()`，退出后立即断言，而非依赖本测试结束后的隐式恢复。

## 必须同时补充或强化的测试意图

1. 在 inner MonkeyPatch context 之外为全部八个根、点分隔 child、深层 child、None 条目设置可辨识 sentinel，并保留近似前缀名；进入 `make_case` 后确认 inherited descendants 消失、八个根由 synthetic ModuleType 占据、近似名原对象不动。clean positive 的 distribution 集合仍精确为八个根，不减少预期。
2. 退出 inner context 后确认此前全部条目的集合及 `is` 对象身份恢复；对正常退出和构造中异常退出都覆盖。异常应在隔离完成后、构造未返回时注入，例如本测试 monkeypatch 的 `fake_module` 在首次调用抛出专用异常。这样可以验证真正 setup failure 的清理，而不是只在成功构造后抛异常。外层 sentinel 设置也由外层 fixture 管理，结束后恢复真实 suite 状态。
3. 对原 unknown-child negative，先用同一 evidence 验证 clean positive，再注入未登记的 child，仍精确期待 `BUILD_PROVENANCE_MODULE_MISMATCH`。保留原 reader 的全 `sys.modules` 扫描和独立 native 校验。
4. 保留原 repeated verification：第一次 clean verify 成功后改 loader code，第二次仍应拒绝 `LOADER_MISMATCH`；不得降为仅检查第一次结果或改预期码。
5. 直接 `make_case` 调用也经过同一隔离逻辑；不依赖测试执行顺序，不改为 only-selected 或跳过全套有污染环境。静态评审阶段不主张这些测试已经通过。

## 后续验证申请范围（尚未授权或执行）

若根接收方案并另行授权应用：生成独立测试候选；先做静态 diff/格式检查及有界 fixture 恢复、unknown-child、positive/recheck 测试，再按实际修改的集成基线安排完整 `npm run check`。如需要因果复现，可在隔离测试中主动预置 sentinel descendants，不靠猜测当前真实库名；保留修前失败及修后结果。不得机械重跑原未修复全套，不扩大到打包、Electron/native/CLI、ABI/loader 实验。是否执行及具体资源窗口以根后续票据为准。

全量原始失败、此前有限通过和本次静态判断分别保留，未形成新的运行通过或发布结论。
