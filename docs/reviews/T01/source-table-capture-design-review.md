# T01 tableDigest r2 独立设计复核

结论：**D1/P2 在设计层已闭合，未发现本次修订新增阻断。** 支持 root 读回后按明确的新 phase 实施；本报告不批准未完成准备 patch 或下一版代码，不构成机制测试、实际 parser 或运行时接线通过。

## 固定输入和只读边界

- 委派：T01 开发者要求 `/root/store_interface_audit` 独立只读核对 D1，只写本新报告。
- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`；HEAD `b35cb4e21d375386775e5fc0431a8089a47195da`。
- 新合同 `docs/iterations/T01/source-table-digest-contract-r2.md`：全文实际读取，SHA256 `e56c09fdae587e15e1beb8cd170998608dc676fc4c4f754eea5c4e162fd3d315`，与委派值一致。
- D1 原独立报告 `/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/T01-controller-source-r4-table-digest-design-review.md`：实算 SHA256 `9da31728abe373a0e6b455f508d4fc4de2459c1e570362674561c7f286868c39`，定点读取 D1 及结论。
- 原 r1 实算 SHA256 `568cb308ec5db6b7b537b4a385958a475c200268d750cedd73bdb1e28ce65b79`；原独立报告实算 SHA256 `240a3d08e834b06a3f7592e69568b26df0f6d8dd1806fa49824343a6fedcf884`。均保持原件，未改写历史结论。
- 仅静态设计复核，未读取准备 patch 或新产品实现，未运行产品或机制测试。未修改实现、测试、旧报告、依赖、配置或 AGENTS，未提交/切分支；不运行 GUI/Electron/e2e/native/HMR。

## D1 四项核对

1. **受控值来源和回调边界明确。** r2 §1 将入口限定为经过实际受限解码/批准 producer 适配、owner 独占的 data-only JSON 树。TS 材料属性必须 own data descriptor，不以访问 getter 获取“待校验值”，不让 toJSON/iterator/强制转换回调参与。Python 要求精确 builtin 容器、键和标量，先 exact type 门后 builtin 访问，拒绝子类和自定义转换协议。sourceHash、options、implementation 同样捕获，不对“可信配置”暗开 getter 例外。
2. **同一计费/编码材料由一次捕获保证。** r2 §2 明确一次有界 capture 后只使用私有原始值及私有容器；局部 row/cell 标量不在计费与保存间重读 caller，编码也不回 caller。异步 hash 之前 bytes 已私有确定，完成前不公开容器。原 r1 的“无 await 因而无变更窗口”推论不成立；r2 以新的数据所有权和 capture 不变量取代它，未继续依赖该旧推论。
3. **捕获自身先限量，sheet 先计费。** 有限字段/行/宽度、键形状和原运输树先验预算是明确前置；新节点/escaped chunk 加入前预留对应编码字节。无单项长度界 sheet 逐码点核剩余额度，超限即停，禁止先 Array.from、全 escape/encode/clone 再判断。私有字符串可引用已经捕获且计费的 immutable primitive，不为解决变更风险再无界复制。输出 buffer 仅按已核精确总长分配并核最终长度。
4. **必要反例与保证范围匹配。** §3 明列 own data 正例、getter 第二读变化/改 options 或其他 cell、toJSON/valueOf/toString/iterator、数组 hole/额外 symbol、Python 子类/自定义协议、caller 后续修改、sheet Unicode/非BMP/NUL、exact budget/±1 和巨大 int/NaN/布尔预算。均标“未运行”，没有将本设计文字算成测试证据。

## 明确接受的边界及下一代码门

JS Proxy 的反射 trap、被篡改 intrinsics 和敌对同进程执行不能由描述符检查绝对排除；r2 已直接承认，要求实际 owner 数据来源保证，必要 CPU/内存抗滥用依原 worker/进程隔离与硬预算。此范围与 D1 原报告要求相符，不以“检测所有 Proxy”作为不存在的保证。

下一实现审查必须看到入口真实来自该 owner 解码/适配边界，而不是 caller 自报 data-only 标记；记录/数组数量检查不能先在未受限对象上建立全量 descriptors 或深 clone。机制测试应以 spy 证明普通 accessor/转换回调 **零调用**，并证明编码只用 capture 后的私有值。恶意 Proxy 反例只用于标识前置/隔离边界，不能用其替代普通 getter 拒绝测试，也不能把未触发某个 trap 当绝对检测证明。

上述是下一代码的验证门，不是本轮新增设计阻断。`ffdde792…5845` 准备原件仍不得直接采用其两遍 caller 读取方案；本轮不认证其内容或静态检查结果。真实 parser 三字段、CSV 编码词汇、合成 golden 与实际 producer 的区别、完整表运输和资源预算、source/确认/Job/Store、公共业务3 ready、包/native、指定双审/CI及父验收继续保留。

本次没有新的代码反例或运行通过声明；D1 关闭仅指合同已充分说明所需数据捕获/预算不变量，最终代码须 root 明确批准 phase 后实施并另作真实验证。
