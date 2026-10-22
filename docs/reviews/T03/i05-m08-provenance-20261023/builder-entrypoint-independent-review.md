# 私有 builder／entrypoint 两路径独立静态审查

结论：入口与正常 buildEngine 调用链的合同方向一致；发现一项只影响导出私有发布 helper 非规范 root 调用的 P3 失败路径，建议修正并在 owner 单元覆盖。当前不签四路径完整候选、完整 artifact 收集或运行通过。以下均为静态推导，未执行实际复现。

## 固定输入

| 输入                                      | bytes | SHA-256                                                          |
| ----------------------------------------- | ----: | ---------------------------------------------------------------- |
| scripts/build-engine.mjs（当前 WIP）      |  8298 | 94a37649cd2471b7140bd6277968aac610bc4d276554a52894b07e24ee8c7238 |
| packages/engine/entrypoint.py（当前 WIP） |   976 | aaf9f85b59f115ae0646fd31f5305ee588c2bd58a0fbb28d9714c707c9035ef3 |
| private-contract-v1.json                  | 36587 | 9d97a6a233b47abc23064a9a8f8330080d62f39b3db981de14a148880e202a04 |

基线 HEAD 为 `2fdd85375300bfbfa797588c348a205e1030ef6c`。已全文读两路径及其 Git diff，合同沿本 agent 前审/差异复核的固定版本。未读写另一 agent 正在实现的 `semantic_build_provenance.py` 或其测试，也未将 helper 未实现行为当已验证。报告完成前重核两文件 bytes/SHA 与首读一致；保留此前两份合同报告不变。

## F1 / P3：独立调用 publishEngineCopy 时，未规范化的绝对 root 可使祖先循环无法结束

位置：`scripts/build-engine.mjs:99–114`。前置仅要求 `isAbsolute(root)`，却用 `while (source !== root)` 停止祖先遍历。`runRoot` 和 `engineDirectory` 都按 `resolve(...)` 定义，`source` 及其祖先因此是规范化路径；未规范化的 root 字符串不会出现于该祖先链。

具体静态反例：root 为一个真实 checkout 的绝对路径加 `/.`，runRoot 按 `resolve(root,'build/i05-provenance',token)` 构造，engineDirectory 同样按规范固定路径构造，且对应目录都存在。这些参数能通过当前前置；source 最终到达 `/`，`dirname('/')` 仍为 `/`，`lstat('/')` 是真实目录，因而不会达到含 `/.` 的 root，也不会触发目录拒绝，形成无限循环。没有运行此反例。

`buildEngine` 在第 151 行先 `resolve(repositoryRoot)`，因此它自身的正常链不受该反例影响；这不是默认 npm 构建已挂起的证据，也不涉及 renderer/public CLI。问题范围限于导出的私有 `publishEngineCopy` API，优先级为 P3。

最小修正：在进入路径比较前统一将 root 规范化，或直接拒绝 `root !== resolve(root)`（并固定字符串类型），再保证 ancestor walk 不可越过终点静默循环。owner 单元可覆盖带 `/.`、重复分隔符等绝对但非规范 root 的立即拒绝/规范化，不能用真正无限循环测试堵住 suite。

## 正常链与失败路径的静态支持

- unique UUID 控制 dist/work/spec/cache，prepare 前检查 runRoot 不存在；`--noconfirm/--clean` 仅指向该新 run 的 PyInstaller 路径，不指向旧 unique 产物。最终 binding 路径位于 artifact 外，没有给 provenance 反含最终 artifact hash 的循环。
- helper 使用 argv 数组与 shell=false；非零/信号或 spawn error 拒绝，stdout 限额与 JSON object 字符串键形状检查后，再要求 prepare/finalize 路径精确等于本 run 的固定位置。finalize 返回 hash 还作 64 位 lowercase hex 形状检查。这里信任的是 Python helper 按合同真正完成内容验证；JS 只检查交接形状，没有独立重算这些文件，不把它说成已审四路径。
- PyInstaller 明确 optimize 0，只有字面 anchor hidden-import 与固定 data 路径；八包 collect-all/metadata、engine data、旧 contracts 和 uv.lock 收集保留。builder 导入私有 Python helper是构建过程，不是 frozen 运行前提前导入语义模块；真实运行 observer 顺序仍由 I05 唯一 probe writer 接线和验证。
- source 目录祖先、staging parent、temp 占位检查使用 lstat，因此不会把 dangling symlink 当不存在；source/parent 的 symlink 与非目录拒绝。没有宽泛递归删除旧 target 或其指向对象。
- publication 先复制到独立 temp，成功后才移动旧 staging 到新 run 的 archive，然后 rename temp 到 staging。copy 失败不动旧 staging；archive 失败不报告成功且新 unique source 留存；最后 rename 失败时尝试恢复旧 staging。若恢复本身也失败，会抛错并保留 archived 对象，不应将该分支描述为必然原路径恢复。JS 没有删去 unique source、旧 archive 或第一份 binding。
- staging copy 与不可变 unique artifact 是不同路径。当前函数返回复制后的 stagingDirectory，不代表复制后目录已被本 reviewer 逐文件核过。root 后续仍必须按合同在真正执行目标处核完整外部 binding；不得拿 unique source 的 binding 未经检查便给后来 staging/packaged copy 签批准。

## N1：当前静态入包依赖仍待最终接线/实证

当前 `--hidden-import` 只显式列 `_i05_private_build_anchor`，而现有 I05 probe 尚无新 reader import（只对旧 probe 的 import/guard 标识作局部读取，未读另一 agent 的新 reader）。`--collect-data ontolearn_engine` 不能作为 Python reader 已在 PYZ 中的证明。因此，这两个路径本身尚不能证明合同 privateModules 的两个模块实际都入包。

这先登记为待集成依赖，不把当前未完整集成候选误报成一个已复现打包缺陷。owner 可显式 hidden-import reader 以使私有 builder 不依赖未来调用可达性；或在最终 I05 接线后由 finalize 的实际 PYZ 核验确认，不允许在缺项时默认为通过。root 已限定最终身份来自最新完整 I05 修复源，当前两路径局部审查不解除这一前置。

## 入口与责任边界

新增分支只在 FLAG 精确匹配时 lazy import 同一 canonical probe，保留原 FLAG+selector，不 pop 语义 FLAG，并以 `raise SystemExit(probe_main())` 传播 int 返回；其余 storage/worker/contract/resources/default 分支在 diff 中未变。未新增任意路径 CLI，也未提前直接导入 reader/native/语义运行模块。实际异常退出、argv 保留和导入顺序仍须 owner 私有单元实测，静态阅读不是实际进程退出证据。

本 agent 仅写本报告并做其格式检查；未修改两产品、合同、I05 probe/test 或其他 agent WIP。未安装、执行产品、Node build helper、engine、pytest、GUI、native 或 parity。F1 修正及必要局部单元后可复核该 delta，但整体实现、root 外部预冻结批准、loader/native/source-package 语义证明必须按完整候选另行验证。
