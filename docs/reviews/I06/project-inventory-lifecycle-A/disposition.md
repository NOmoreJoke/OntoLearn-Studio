# I06 A 冻结处置与验证记录

2026-10-21。本地分支 `feature/I06-project-inventory-lifecycle`，批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。四个产品/测试文件与 A 说明的精确身份见 `inputs/frozen-code-before-final-check.json`；最终 check 后逐字节复核一致。提交身份由实际 Git commit 提供，不在提交自身制造自引用 hash。

## 结论与实际工程验证

两项独立纯机制模块及两项专属测试已完成。独立审查原文 `independent-review-final.md` 确认四项 P2 均已关闭，无新增阻断。审查形成时尚未获得最终 check 终态，其原文保留原时点；owner 此后实收下列终态：

| 实际记录                            | 结果                                                                                                  | 适用候选                                |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `raw/specialized-after-all-fixes.*` | exit 0，70 pass，0 skip                                                                               | 最后逻辑修复后；cohort 后续仅补寿命注释 |
| `raw/full-check-final.*`            | exit 0；17 TS 测试文件、700 TS 测试、1052 Python 测试通过；正常 lint/format/typecheck/build/ruff 通过 | 精确绑定冻结的最终五文件                |
| `raw/sources-final.*`               | exit 0，12 个归档源文件通过                                                                           | 同最终候选                              |

所有命令 cwd 均为本新树，精确 argv/exit 见各 JSON；原 stdout/stderr 分别保留。新树独立执行 `npm ci` 与 `uv sync --frozen`，各 exit 0；没有借用或复制其他树的可变依赖环境。完整 check 自带无窗口工程构建，不是 Electron/native/端到端或平台运行证明。

## 四项独立问题与原始反例

1. **导出 owner 集合可删改。** 运行时冻结固定集合，不能删去必需 owner 伪造 complete。
2. **重新观察丢失迟到 release。** 保持稳定内部记录与出生 owner，仅替换不可变 metadata，迟到完成归于原记录。
3. **原 Promise 重用于另一数据库释放。** 工厂 WeakSet 记录成功登记的原 Promise，终生一次性归属；结算或 profile 变化不允许复用。
4. **结束的 child/Store 聚合寿命仍能发布或接纳。** candidate/active 聚合寿命终态立即 quiesce 并失效发布；已 draining 的实际正常结束仍进入释放。明确这是整个 cohort 永久拥有关系的聚合寿命，普通同 Supervisor session 恢复不触发本路径，也不由 A 认证 session-ready。

首两项红测先保存 `inventory-independent-red.*`（1 fail / 33 pass）。其中可变集合测试的观察顺序不足以复现，修正测试为先登记两 owner 再观察后，`inventory-independent-red-both.*` 实际 2 fail / 32 pass。首次结果没有删除或改报成两失败。其源码快照 `inventory-before-independent-fixes.ts.txt` 已含另一个 clock 异常补正，SHA 为 `18439a02ee2db51bcb8b21bc14f674cefbed1d49e7f870c0450c3845dd98c27e`，不是最早独立探针审读的 c885 候选。

第三项在 `inventory-before-promise-fix.ts.txt` 的 1018 候选上实际 2 fail / 34 pass，见 `inventory-promise-red.*`。第四项在 `cohort-before-lifetime-fix.ts.txt` 的 a9bf 候选上实际 4 fail / 30 pass，修复后 34 pass，见 `cohort-lifetime-red.*` 与 `cohort-lifetime-green.*`。随后两文件组合 70 pass；最终完整 check 复跑最终代码。第一次完整 check 的 694 TS / 1052 Python 通过仅属于中间候选，不代替最终 700 TS 结果。

两次独立内存探针的完整脚本、工具合并输出及采样限制保存在 `independent-inventory-first.txt` 和 `independent-second.txt`。它们均 exit 0，但 stdout/stderr 未分离，不补造分流原件。独立审查原文保留这一限制。

初始 inventory lint 的 no-control-regex 失败保存在 `inventory-lint-first.*`，改为字符码检查后正常检查通过。cohort 初始两处 prefer-const 与 MAX_VALUE 时钟反例失败保存在 `cohort-agent-first-failure.txt`；它是当时工具输出的转录，缺少独立 stdout/stderr 与逐命令 exit，不能声称是逐字节进程原件。后续原始统一检查另存。MAX_VALUE、clock throw/rollback、Proxy 捕获耗时与 publish 前过期均有相应机制检查和回归。

## 原件包与复核方式

`evidence.zip` 收录精确四产品/测试、A 说明、startup、两份授权/独审输入、冻结输入、独立审查最终原文、本处置文档及全部 raw 记录。ZIP 不含自身、外层 manifest 或之后的 packaging-verification，避免递归与自引用。包成员均采用仓库相对路径，可逐成员解压后对照 SHA256；不是可运行依赖或用户数据包。

外层 `manifest.json` 列每一原件和 ZIP 的字节数、SHA256，明确 ZIP 成员清单；manifest 不自列。`packaging-verification.json` 单独保存实际解包 CRC、成员集合/逐字节 hash、最终输入绑定和范围复核结果，不纳入自身或 ZIP。打包前后不修改四文件；原始日志末尾空行保留，任何 Git whitespace 提示不通过清洗证据消除。

## 保护与未验边界

只新增授权四文件、`docs/iterations/I06/project-inventory-lifecycle-A.md` 和本 review 目录。最新 AGENTS 15852B/SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 保持受保护、未 stage；没有修改共享宿主、Store、canonical、旧测试、锁、配置或 build/CI。原 I06 树 HEAD `1f3b053d8a69d1f7ddb1e29c143f648d910fe689`、961 树 HEAD `961ce77f26accd11bd1cd3ad4a9e560cd3565e37` 均仅 AGENTS 未提交，未写其产品/证据。

本结果始终 `mechanismOnly:true`、`productionAdmission:'unsupported'`。真实 owner/retired 来源、FS/原生句柄、SQLite/VFS、T01 Store/worker/宿主及公开消费、目标 Windows/macOS 均未由 A 接线或验证。无 GUI/native/e2e/HMR/Keychain/模型/付费调用、push/PR/merge。B/C/D/E、指定 GLM-5.3 最高与 M3.1-Flash xhigh 同候选双方新审、平台、CI、正常 develop 合并和父 I06/FR-002 门均未关闭；原 Goal 状态未改变。
