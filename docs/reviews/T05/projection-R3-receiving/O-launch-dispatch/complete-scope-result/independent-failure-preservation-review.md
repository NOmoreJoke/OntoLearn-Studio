# 原 M 完整范围续接失败保全：独立收件复核

**限定 Pass。** 本批7件已收静态副本的字节、失败目标、时间关系、缺报告状态、错误候选限制、来源保护及未发送恢复范围相容，未发现需要更正的内部矛盾。该结论仅确认失败保全材料，不是产品复审、失败根因判定、恢复受理、完整审查完成或任何父门通过。

## 范围与方法

任务给定主树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-source-package-oracle`，基线标识 `b4b3e2287a9db7e460cab64eab4d71456ac08da9`；本次未调用Git另验HEAD。仅读取本目录7件冻结输入，并对照前批 `post-intake-terminal-readback` 已收checker、保护快照及3538B续接准备稿。唯一写入是本报告。

README、237B短继续及三个较小JSON均全文阅读；四个JSON全部完整读入并严格解析，拒绝重复键与非有限常量。较大保护快照逐项核对必要标量。checker仅以字节与前批相同脚本核同，未执行。未跟随source/native/DB路径，未进入任何模型工作区、GUI、产品、测试、网络、Goal或原因追查，也未等待后台。

## 核对与准确性意见

1. **失败目标精确，没有用fallback代替。** `current-delivery-terminal-projection.json` 的本人sid为 `mvs_8262fb931cf34f3dae99b85683d65fd7`；精确runtime结果只有一行，turn为 `turn_task_delivery_c9786ac29b604f11be3bc40ea7235f4a`、`terminal_outcome=failed`、updated `1792682324377`（15:18:44.377Z）。fallback数组为空，观察为15:21:41.596143Z。公开错误归因副本的sid及failed turn与之完全相同。
2. **旧续接turn仍未核终态。** 原 `ad9639fb-848c-4b3d-9367-a29c8f46420a` 的已收末assistant标量仍为toolUse；README说明未找到stop且runtime当前投影被交付turn覆盖，receipt写 `unknown-covered`。这些材料没有给原turn正式终态，本报告不以新delivery failed替换原turn。该“未找到”的来源自述未由本人重查native；这里只确认副本明确维持UNKNOWN。
3. **缺终稿没有被制造成成功。** 15:22:19.278330Z的receipt只记录声明的 `launch-O/final-v2.md` 路径 `exists:false`、fullScopeCompletionProven false、ownerDidNotRetry true；时间晚于runtime失败及其观察。README明确未产出final-v2、未制造草稿或成功流；前两版旧报告保留不等于新完整终稿。本人未访问该路径追验，因此该不存在状态仍是此时点已收观察，不是对以后状态的断言。
4. **公开错误候选不能升级为terminal原因。** 归因副本声明仅该精确turn共159条native行中有一条公开toolResult错误：`msg-uebSNGUgDJaPNsxelXgkExcsU-wBVWQkUsR2eXrzZb4`、`call_01a1642bf61872009aa6e53e`、timestamp `1792681966355`（15:12:46.355Z）。裁剪正文实际UTF-8为142B，含 `TypeError: 'int' object is not iterable` 与exit1；不含真实工作区路径、配置或私有载荷。错误候选数组用 `json.dumps(..., ensure_ascii=False)` 的默认分隔符序列化恰377B，小于2KiB；紧凑分隔符会为366B，不能把不同序列化长度当内容矛盾。
5. **候选错误之后仍有同turn assistant。** 公开错误副本与terminal projection中的同turn末assistant，其messageId、turnId、timestamp `1792682292927`（15:18:12.927Z）及toolUse完全相同。顺序为15:12:46.355工具错 → 15:18:12.927后续assistant → 15:18:44.377 runtime failed。它仅说明该较早工具错误不是已证明的terminal失败根因；本报告不推断它与最终失败有无因果。两receipt分别写原因unknown、unknown-not-in-approved-scalars，相容，亦不证明是产品、传输、额度、认证或actor问题。159条与筛选方式是已收自述，本人未重读native验证条数或扩大归因。
6. **142B更正已如实保留。** README明确上一通知曾误写147B，本批实际为142B；独立计算142B与JSON一致。该处按当前真实字节更正，旧误报没有被掩盖，也没有因该工具错给产品定缺陷。错误归因JSON观察15:33:21.217007Z，晚于失败与缺报告观察；时间不存在倒置。
7. **失败后保护快照保持限定。** 本批4472B checker SHA `58807b1a72415745e6f542b816d8922e593cd26cec4d1c91e426e0b673075647` 与前批逐字节相同。15:23:09.112519Z保护快照晚于失败/缺报告，两模型各290个唯一保护path及11冻结launch成员，保护记录与前批完整相等；detached86df、index空、tracked仅AGENTS的投影一致。Z额外32项、M38项均仅path/stat等字段，attribution unknown、contentReadForThisInventory false，wholeFilesystemFreezePass false。不能据名称归属或读取未知内容，也不能推出全FS冻结或所有后台停止。
8. **短恢复仅准备，授权边界没有扩大。** `normal-same-scope-resume.md` 为237B/SHA `bc47e1bea99cf0c7600c538c38533edc26cdce6d178c6d9819f3644ab5d82b39`，全文仅一句，沿此前3538B原范围、冻结来源及全部约束，保留真实失败与两版旧报告，补剩余覆盖/本人意见/子审，另写final-v2且不预设改判。前批所指准备稿3538B/SHA `346e269aa5f76ebe6a85aa80b79761188f2dccc775585cf04f3060daadb07c1a` 核同。README把普通中止/无公开细因且本人任务匹配idle时的一次短继续放在总控下一GUI窗口；额度/认证/付费横幅则走既定负责人和官方流程，不新增购买。准备文本没有自行新scope、换模型、新session或重置，也不要求先证明传输原因。当前材料没有发送receipt或GUI lease；README明确尚未发送，本报告不把准备当受理，更未替owner发送。

没有新增需修改的准确性问题。所有结论以这些已收时点副本为界，不独立证明源runtime/DB/native查询的真实性，也不重做产品审查。原约55件覆盖缺口、11条技术意见、137 pending、26 allocation缺件、完整双审和全部父门继续保持未闭；后续恢复、正式同turn终态及final-v2须单独收件。

## 最终7件输入指纹

7 inputs, 185213 bytes; fingerprint `3da3931f9545c74068eec08c8022b96f94389bc7f3855894c10175598c621eba`. Algorithm: sort by filename, concatenate UTF-8 `name<TAB>bytes<TAB>sha256<LF>` for all inputs, then SHA-256. This review and any later delivery manifest are excluded.

| Input file | bytes | SHA-256 |
|---|---:|---|
| `README.md` | 3256 | `af171359cd73737a1d4e2791fdd107bf7dc2028ed723c89c2765490f57848bf3` |
| `check-protected-stat-only.py` | 4472 | `58807b1a72415745e6f542b816d8922e593cd26cec4d1c91e426e0b673075647` |
| `current-delivery-terminal-projection.json` | 1087 | `a995559dcf7d27be6cfd4c6c039035d2962ae99429a1ae77b40d43c8cd0a89ff` |
| `exact-delivery-public-error-attribution.json` | 1566 | `8574c39c26e37bc3416c7458eadfd6fa7ae6893e95a1b95ba1ecaa0d5faee31b` |
| `final-v2-failure-receipt.json` | 448 | `a50c4337234b45b17fa6c8c8e9ac2e6cae41d17407eb940a96420e21befd68fc` |
| `normal-same-scope-resume.md` | 237 | `bc47e1bea99cf0c7600c538c38533edc26cdce6d178c6d9819f3644ab5d82b39` |
| `protected-stat-readback.json` | 174147 | `2bba5bed5fbdab408cb41d040cd63c05b7dfd9c72c82bcb7d2657066106ed2e8` |


对照仅限前批已收副本：checker4472B/SHA `58807b1a72415745e6f542b816d8922e593cd26cec4d1c91e426e0b673075647`；保护快照173858B/SHA `3f0aff26ef64969b23058e4bea4114e6dc2395e045803be7bbb209304e3e2679`；续接准备稿3538B/SHA `346e269aa5f76ebe6a85aa80b79761188f2dccc775585cf04f3060daadb07c1a`。未访问其source路径。
