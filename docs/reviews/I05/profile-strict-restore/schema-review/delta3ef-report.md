# I05 strict restore 最小 S2 delta 独立复核：3ef2f69

结论：**本范围有限通过。S1 保持关闭，S2 已关闭；未发现这次最小 delta 的新阻断。** 成功路径仍通过唯一 outcome 转移完整 children；失败的最终 receipt 路径不再从公开 traceback 帧保留恢复结果。首轮 bbd 和131的失败报告、原始探针及运行证据保留原样。

本报告仅复核131→3ef的最小清理 delta 和必要上下文，不重新审整份方案；费用数学证明、指定双方/CI及正式集成门由各自 owner 负责。

## 固定对象

- 新候选：`3ef2f6952ed1a4f852da31c0bef7e8d8679752a5`
- 父候选：`1316050a895a787b7b94bbe18e99efcb3cd141d2`
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- manifest：`candidate-3ef2f69.json`，旧 `candidate.json` 仍绑定131，本审没有改写。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| `semantic_profile_restore.py` | 50276 | `aa3d51c1ccc487ce21a78560ad6cdf7a6485cc86f746c29ee329e6a0bc4c4d09` |
| `semantic_profile_restore_budget.py` | 37478 | `593b2a832dd510063bb60d7b3d5526fbd6cf4dcba53ad9c513e82dbfdd77ef7f` |
| `test_semantic_profile_restore.py` | 33681 | `d3726f6170d126f7a6b495f53b951093faf0b3caa935b3d87a06c18c25619aac` |
| `test_semantic_profile_restore_limits.py` | 21089 | `4eed5e316f0033080b3f2761b83ddcd53f093f18a6e2aa48706619d109872a8c` |

固定 Git、当前文件及 manifest 的72项均逐字匹配，包含68项保护输入。budget 和 main 测试与131完全相同，S1 的 `_check_expectation()` AST 完全相同；四个源码/测试文件 AST parse 通过。审计记录在 `delta3ef-audit.json`。

## S2 关闭依据

实际修复位于新 `semantic_profile_restore.py:1189–1192`、`:1254–1269`：

1. 在进入 try 前初始化 `children/parse_usage/caps=None`，涵盖 `_restore()` 尚未返回的失败路径。
2. finally 首先把这三个独立结果局部全设 None；存在安全 error 时同时清 outcome。constructor、usage、peaks 三处异常都在同一 try 内，先经安全异常转译，再进入该清理。
3. decoder 的 native 子树/cache 正常 drop 后置 None；terminal cleanup/finish 自身若异常，也清 outcome/decoder 再抛出。没有把异常中的已恢复结果作为部分返回值或额外异常字段保留。
4. 成功时只清独立局部，保留 outcome 强引用。因此 outcome.children、各 child 和其中的 fresh PV 在 cache drop 后仍有成功结果持有，最终按原路径返回。usage/peaks 快照之后仍仅做清理/终态迁移，没有新增计费或峰值预留。

新增 limits 测试在真实 capture 下分别对最终 `RestoredBatchSet` 构造器、ledger.usage 和 ledger.peaks 注入 MemoryError，验证：有限 RESTORE_INTERNAL、无 context/cause、failed/live零，以及公开 `restore_profile_batches` 帧中 `children/parse_usage/caps/outcome/decoder` 五个局部均 None。原成功、原expected/hash污染拒绝、末 child checker 失败测试没有删除或放宽。三项新故障测试包含在下述实际完整测试中。

本 agent 另以标准库运行固定原公开入口 AST，使用原 canonical RestoreLedger，只模拟私有 `_restore()` 的成功返回：三处故障均重现上述五局部全清、failed/live零及无异常链；成功分支 ledger.success/live零，outcome 保留原 children tuple 和 child 的对象身份，formal_authority=False。此探针保存在 `delta3ef-audit.py.raw`，结果在 `delta3ef-audit.json`；它是独立入口分支证据，不冒充完整引擎测试。

## 必要影子变化复核

- 产品 delta 只改公开入口的局部初始化、finally 引用清理及 terminal 异常清理，没有改变 schema、PV parse/比较、source/witness、原allocator/L、disabled/实际空 batch、原 false/true 顺序、16c 调用次数或费用上限。
- S1 早期 exact 容器/成员前门保持与131相同，未重新出现使用 foreign 协议后才核型的路径。
- 所有 wire/PV/source/rows/canonical 检查仍先于16c，各 slot 仍一次、同原 L；成功结果的构造仍在 running try 中，最后统一终态后才 return。
- 不将 cleanup 的 logical live 零单独当作真实引用消失的证明：本次同时检查公开帧的实际局部清理，并有完整引擎故障回归。

## 已读回的真实运行证据

以下运行由父审执行，本 agent全文读回 stdout、stderr 和运行元数据，再逐项检查 source 绑定；没有自行重跑产品测试或共享 Python 环境。

两次运行的全部73项（72项候选文件及AGENTS）前后字节/哈希均核对新 manifest 与当前文件相同，完整绑定记录在 `delta3ef-audit.json`。

| 运行 | 实际结果 | 版本/日志核对 |
| --- | --- | --- |
| `runs/08-final-npm-check` | exit0、无超时、stderr空；lint/Prettier/typecheck、15文件630 Vitest、vite build、ruff check及212文件format、pytest **2873 passed**（包含两个restore文件全部145例及三处receipt故障）。 | HEAD=3ef；72项 source 在运行前后均等于新 manifest；stdout8817B、SHA `b1fff6daaa0e926c506e0d9331495c01ed049c348efb252d95b415ce85b89cb2`，元数据/实际日志一致。 |
| `runs/09-final-verify-sources` | exit0、无超时、stderr空；已核对12个归档源文件。 | HEAD=3ef；72项 source 前后均匹配；stdout111B、SHA `1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536`，元数据/实际日志一致。 |

本 agent执行的检查仅为固定 Git/manifest/current72项哈希、四文件AST，以及上述三故障/成功入口 AST 分支探针。没有新增依赖、修改产品/测试/68项输入/AGENTS、操作Goal、提交或切分支。诊断脚本以 `.py.raw` 保存，不进入全仓 active Python 源扫描。

这份有限通过只关闭本独立 schema/重新发行/原子性审查中已发现的 S1、S2。它不替代预算独审、指定GLM/MiniMax双方新审、CI、目标平台或正式 selected/producer/Store/worker/权限与生命周期验收，也不表示父Goal或上线完成。
