# I05 M06 实际应用后独立窄复核

结论：本次已应用差异未发现 P1/P2 问题；缺 counter 的稳定失败前置与新增反例测试范围合理。作者保存的单例红/绿证据有效，现有十条 lint 失败和两源 format 失败如实保留，不能据此宣称整体检查通过。此为 M06 应用后差异复核，不替代下一新候选的完整工程双审或产品验收。

## 固定对象和实际差异

tree 为 `.worktrees/I05-retained-source-review-triage`，实际 HEAD 仍为 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64`。实际两源身份均与明确授权的精确补丁一致：

| 路径                                                                  | bytes | SHA256                                                           |
| --------------------------------------------------------------------- | ----: | ---------------------------------------------------------------- |
| packages/engine/src/ontolearn_engine/semantic_source_package_probe.py | 93915 | 43d083eebefbf315509d5fb6276369506dd760006264afd076d754ab3b027230 |
| packages/engine/tests/test_semantic_source_package_probe.py           | 73863 | c99a6acc40ab9c612a906cc72db336c9079a41c6fa8d2aa53b7c0c5c72b80752 |

独立读取这两个固定 base blob、计算当前身份，并获取固定 2cf 到当前两源的 diff。结果与作者 `m06-final-source-diff.stdout.raw` 的 1794B 完全一致。移除新增 guard 和新增测试后，余 AST 与固定 base AST 完全一致；只解释 `_scope_observation`、ProbeFault 构造、probe fixture、新增测试及单个 scope 调用关系，没有扩审其他算法。

`_scope_observation` 当前在第一条语句检查 `counter is None`，以既有 `ProbeFault("INTERNAL_ERROR")` 拒绝；ProbeFault 的现有构造接受 code，并只保留受控 ASCII code。检查在 modules/dataset 查找与 canonical parse/prepare 之前，不制造业务成功或默认 counter，不给正常 non-None 路径增加后续行为。实际 scope 调用点仍在原调用关系中；本审查不重判旧意见所述“缺 counter 在现有合法路径不可达”的整体证明。

probe fixture 返回实际导入的 probe 模块。新增 case 以空 modules/dataset 和 None counter，要求准确 ProbeFault 及 INTERNAL_ERROR，能暴露 guard 缺失时抢先 KeyError 的反例；它没有伪造 canonical 业务返回。

## 保存证据与证明边界

独立核对十三份授权命令收据及所指真实 stdout/stderr 的 bytes/SHA。没有复跑作者命令。

- 红流 `m06-regression-red-01`：exact nodeid，实际 exit 1；失败是缺 guard 时 `modules["ontolearn_engine.semantic"]` 的 KeyError，stdout 1586B、stderr 0B。
- 绿流 `m06-regression-green-01`：同一 argv/nodeid，实际 exit 0；stdout 98B，明确 `1 passed in 0.12s`，stderr 0B。
- 环境收据 exit 0，记录本 tree 自有 `.venv`、独立 cache 和 linkMode copy；真实流显示 CPython 3.12.12、本 tree engine build 与 `.venv` 创建。未进入其他 tree 环境或原生/全局元数据验证 cache 行为，隔离属性以该明确收据为据，不作超出保存流的实证声称。
- 作者 whitespace 收据实际 exit 0。独立固定 base diff另行保存于 `independent-triage-r1-applied-diff.stdout.raw`。

绿色只证明这一个缺 instrumentation 的早期拒绝分支。它不触及 canonical 加载/语义正确性；旧锁环境能跑此例不证明 M08 pyshacl 缺口已修复。没有本次合法 full-v1/B1/full417、canonical 集成、source/package 对照、打包、native、DB 或发布验证。不能从 AST 不变或此单例外推完整合法路径已通过回归。

## lint/format 失败保留

| 保存检查                                 | 实际结果                            | 窄复核结论                                                                                    |
| ---------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------- |
| 当前两源完整 Ruff check                  | exit 1，10 条                       | 1×I001、9×B023，整体未通过                                                                    |
| 固定 2cf 两源经同工具 stdin 的 Ruff 对照 | probe exit 1，test exit 0；合计10条 | 按准确插入行映射比较 code/message/location/end_location/filename，十条签名全等；本次新增诊断0 |
| 当前两源完整 Ruff format check           | exit 1                              | 两源整体格式检查未通过                                                                        |
| 固定 2cf 两源各自 format check           | 各 exit 1                           | 格式失败在旧字节已存在                                                                        |
| 新增 guard/test 片段 format check        | 各 exit 0                           | 只说明新增片段符合该工具格式                                                                  |

probe 的诊断位于插入点之后，对照为准确 +2 行；测试新增 +8 行，旧 test 本身无 Ruff 诊断。没有把整体失败涂绿，也没有批量格式化或修复继承 B1 区域。149038B 大 format 原流保存并核对完整 bytes/SHA；未为显示截断编造“全文显示”证明，也未借该流扩读其他算法。

## 原审查与后出登记

原主报告 7513B / b205c2cafc300e0f1e4da72e000046d6b22d3343d45fe55d771d27bb0a11d8b0、原未应用提案补充 1543B / 886b539fc1367fed50b171abc3c86a0f52baeb6e4c6180951c9185b9b742e81d 均经身份核对保持原字节。本轮未重跑六输入静态 checker。

`triage-disposition-r1.md` 已后出明确“锁缺五个，含 pyshacl；engine runtime 闭包缺六个，另含 packaging”，并保留 M08 实际缺口与运行前置条件。原 P3 R1-P3-01 的历史发现仍保留；歧义已有明确处置，不改旧六输入或原报告。原 `m06-unapplied-proposal.*` 继续表达提案时点，而实际应用证据另存，时间边界正确。

## 本次独立操作和限制

新 stdlib 检查器 `independent-triage-r1-applied-check.py` 实际 exit 0，stdout 272B、stderr 0B；双流与真实 exit 收据按同前缀保存。仅执行固定 git 身份/两源 diff/blob 读取和 stdlib 字节、JSON、AST 比较，没有执行产品、import、pytest、uv、安装、Ruff、npm/fullcheck、DB、native、GUI、Goal、CI 或外部模型消息。格式检查仅针对本次新建 applied MD/JSON 使用指定 Prettier，收据另存。

本轮只新增 `independent-triage-r1-applied-*` 文件；没有 stage/commit、产品写入或修改原封审报告。T03/T01 路由及其他旧意见、完整工程/运行/发布门保持原边界。
