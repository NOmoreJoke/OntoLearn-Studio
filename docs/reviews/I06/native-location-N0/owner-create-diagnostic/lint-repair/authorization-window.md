# I06 诊断候选：既有单测试 lint 修复增量

2026-10-22。总控实际读取2d/2de79诊断交接、完整check原双流和TS189上下文，确认check唯一阻断为未改动 `tests/unit/i06-native-location-owner.test.ts:189` 的prefer-const，不能把其余阶段通过称完整check通过。该旧文件当前SHA256 `e0946f7daf1236045d0198d989cf718ea40227d63b76e5a1407eaa1b0d501b04`。

现给原I06唯一新增writer：上述TS文件，只在“does not publish a late wrapper after reentrant revocation”这一测试删除提前的 `let current: ReturnType<typeof owner>`，将原赋值位置改为 `const current = owner(data.binding)`；保持mock安装、owner创建、调用顺序及所有断言。不得把owner创建前移、禁用lint或更改测试预期。其余源码/九源中的其它路径、30037B诊断C++及所有旧原件保持。

继续原树/分支，从纯过程2de79e886bb9fb3aa97cb66efc1d04a86961c552起点，只提交此TS最小修复为新候选。实际新差异后按AGENTS跑一次完整check和12源核验；保原完整check exit1，不覆盖日志。独立agent点读此两处声明差异并核实际检查和新固定九源指纹即可，不重审旧N0或重复无变化C++验证。

过程追加到owner-create-diagnostic的新lint-repair子目录，旧报告/清单不改。回新产品/过程、C++与TS两个精确供方pin，根再给T03必要新采用/构建；当前不授权构建或任何native再运行，不扩大源/断言/限额/清理/系统权限。原owner-create实际根因仍未知，不能由lint修复宣称已解决。
