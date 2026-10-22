# I05 diagnostic-result-r1 独立静态复核

结论：Limited Pass，仅针对新增复现证据和 dict 消费断言修复，未发现新增 P1/P2。两份原始 JSONL 独立核验支持“这次新增的 A/B 运行在相同 observation/API/stage 首先失败”；这不恢复也不替代 T03 首次未落盘的 BytesIO。dict 修复具有固定公开函数返回结构依据，保留原业务期望，尚未在修复后运行。

## 新复现的直接证据

只读取根协调者明确授权的 11 份诊断文件、其中指向的 2 份原 observations.jsonl，以及两源文件/其 d1fb 基线 Git blob。未沿 parse_turtle 跟入共享算法。完整输入身份见 receipt-diagnostic-result-r1.json。

原始 launcher 收据记录：2026-10-22 18:06:10.389593–18:08:57.776840 UTC，实际 exit1，launcher elapsed167.386965s。pytest stdout 原字节独立读到 collected2、2failed、166.16s；两个耗时属于不同计时范围。stderr 是原始零字节文件。没有把实际失败改写成通过。

| 新运行 | 原 JSONL bytes / SHA-256 | 记录 / 已完成 / 未开始 | 首次失败 |
| --- | --- | --- | --- |
| shared | 16560553 / `3b1b290b76212309af9e5e5a19bffd4dec3a077ba8bed1d6923ec7afd7cb8834` | 156 / 154 / 263 | turtle/front-5；parse/turtle；semantic.parse_turtle；INTERNAL_ERROR |
| producer-fault | 16560566 / `d9598c2326a8b39a02d476abb059f45b14abd1787055ebbfb70d1cdb5b2d0300` | 156 / 154 / 263 | turtle/front-5；parse/turtle；semantic.parse_turtle；INTERNAL_ERROR |

对两份原字节分别完成如下纯静态检查：全部物理行可解析；1个 header、154个 observation、末尾 terminal；仅1个 unexpected-failure，且为最后 observation；该失败与单独 failed-observation 提取文件对象完全相同，terminal 与提取文件对象完全相同；所有 observation id 严格等于 completedIds；completedIds 与 unstartedIds 的串接严格等于 header 的417项 selectedInventory；报告/单物理行均未超过64MiB/32MiB上限。

两份失败记录均为 Exception、classification=harness-or-unknown、parse_turtle attempt returned=false，partialOutputs=[]，reason/validator计数都0。终端 state=failed、collectionComplete=false，记录的首败是 INTERNAL_ERROR，而非 COLLECTION_DEADLINE；各自 terminal elapsed81.806147s/83.599601s。它们不是用“pytest总耗时长”推测的 timeout。

已观察区间没有任何 dag/fullview/restore-negative 操作，其相应 id 留在未开始区间。因此在这次新复现里，producer-fault 的恢复故障注入目标未被运行到；不能用这个失败声称 capture/restore 故障保持逻辑已被验证。

这些证据定位到 canonical parse 调用边界，但没有解释为什么 parse_turtle 抛 Exception。没有原异常私有细节，也没有读取共享函数实现；底层拒绝异常是否应映射、是否存在适配错误等仍未裁定。更没有证据把这次首败反写成 T03 首轮的实际 firstFailure。两次新运行的同首败可支持下一步定点调查，不能据此宣称前7项历史失败都已获同一根因证明。

## dict 断言修复

当前测试：75493B，SHA-256 `b81d474d391a629c22969ad290607c5f5099ce041238ca9b5bf96b43a902fab3`。本次真实诊断运行绑定的测试是此前75647B/`4fdc5c954c7784ca17298da4e23cbe77d7a618cfeb93add29cd074a13285a39e`；当前字节是诊断之后的修复，不能说它已被该次运行覆盖。

相对 d1fb 基线，当前测试仅包含此前审过的诊断落盘，以及原3条属性断言改成2条精确映射 tuple 断言：

- roots 必须精确等于 `({"kind": "step", "ordinal": 0},)`。保留原唯一根、step、ordinal0，并进一步限定 tuple 和键集合。
- all_roots 必须精确等于 `({"kind": "step", "ordinal": 0}, *expected_premises)`。保留 step/leaf/leaf 顺序及原两条 leaf 引用；expected_premises 的构造和所有生产、字节、restore、负例断言均未变。

精确逆转新增的两个 tmp 参数/五条落盘语句和这两处3旧断言→2新断言改写后，整个测试文件 AST 与 d1fb 相同。probe 仍与 d1fb 字节完全相同：102669B，SHA-256 `05f4ac85f883f40142782e9ee3943b8df9593ddf5a35e318ca35bbd6781a6dd4`。没有改417清单预期、selector、guard、identity、公共错误或共享实现。

根提供的 roots-return-layout 与本独立审查此前直接抽取的固定2cf函数一致：explanation_roots 1743–1750 行构建 tuple，leaf公开映射为kind/reference、step为kind/ordinal、其他为kind/firingIndex/headIndex，1767返回；内部RootRef不直接公开返回。此次修复因此更正消费形状，未降低原业务期望；不需要改变公共接口。它仍需主 agent 的后续实际验证。

## 身份与限制

diagnostic-binding-01.json 声明供应商4e752177及六个输入身份。独立审查先前记录的诊断测试/probe身份与该绑定匹配，本次静态核验原JSONL及提取一致性；没有重新读取许可窗口外的 manifest、lock、build、AGENTS，也没有声称独立见证整段运行期间六文件不可变。result中“运行期间源码未变/六哈希复核”等属于主 agent 收据陈述。

本轮未执行 pytest/canonical/full-v1/B1、Ruff、formatter、安装器或 GUI；只执行 Git、stdlib AST、JSON与字节/hash检查。没有重启、kill或改变运行参数的动作。所有旧报告和旧产物保留，仅新增 diagnostic-result-r1 后缀文件。本报告不构成完整 check 通过、共享异常根因关闭或整体验收完成。
