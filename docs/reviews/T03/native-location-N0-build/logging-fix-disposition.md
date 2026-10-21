# R5：命令异常历史追加修订

2026-10-22。根在固定 c7ca9f517d3a4cffc39ce823b8f0bb16091e68a5 独立预审新增 R5/P2：先 open 双流、spawn/finally-close，返回后才建 record 的旧路径，可能在第二 open、spawn、任一 close、验证或日志写入异常时丢本次命令历史。原 R1 的执行布尔修复不能覆盖该缺口。原 c7、R1–4报告及全部 raw 保留；本项另行处置。

仅改 `scripts/build-native-location.mjs`，CMake/lock 保原字节。候选 `R5-logging-1` driver27002B/SHA `d1ddcbd699be1feccd85a39ec583bcab6563d08597f70df5ad430f9879f06714`。三个 writer 身份见 `logging-fix-candidate-1.json`。

- 全部 planned executable/argv/cwd/双流路径在任何 open 前写初始日志。后续生命周期写独占递增 snapshot，不覆盖旧字节；失败快照可能部分写入，保留并明确未持久。
- open、spawn、两个 fd close、输出验证和日志持久化分别处理。第二 open 失败仍尝试关闭已开的 fd；close 独立，不重试结局未知的 fd，也不阻另一 fd 清理。
- dispatch 前落盘的是 intent，attempted=null/start unknown；调用边界与返回/同步 throw另记。只有返回的正 PID 是已观察子进程证据，尝试不等于启动。
- run 的 status/signal/error 在 cleanup 前保存并登记早期失败；firstFailure只赋一次，cleanupErrors另列。后发生的close或日志错误不能覆盖早期spawn失败。
- 任一持久化失败均禁止继续下一 dispatch，尽力向stderr回退完整有限log、最新成功snapshot和真实执行结构。外层异常也保 buildDir/当前计划/历史/首因。日志和stderr本身都可能失败，不保证持久性、进程终态或资源drain。

实际静态验证见 `logging-fix-static-validation.json`：Node --check0、源码/JSON格式check0、六target/component实际verify-only均incomplete/2，writer检查前后相同，未生成native build目录。未执行futurecomplete、故障注入、--build、configure/compiler/native测试；独立材料窗口的限定版本探针另记，不与这些验证混用。API3候选未升级为实际最低API通过，全部原审批仍false。独立复审报告另保 `logging-fix-independent-review.md`。
